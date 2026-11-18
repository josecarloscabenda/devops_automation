# Docker no WSL ↔ Docker Desktop — como está montado

Notas do meu ambiente, levantadas diretamente da máquina em **2026-11-18**.
Complementa a secção 5 do [`MEU-SETUP.md`](../MEU-SETUP.md) (troubleshooting e Resource Saver).

---

## 1. Resumo em 30 segundos

- **Não há Docker Engine instalado no Ubuntu.** Nenhum pacote `docker`/`containerd` via `apt`,
  e o `docker.service` está `inactive`.
- O **engine** (o `dockerd`) corre **dentro do Docker Desktop**, numa distro WSL própria chamada
  `docker-desktop`.
- O Ubuntu só tem o **Docker CLI** (o client), injetado pelo Docker Desktop através da
  **WSL integration**, e fala com o engine por um **Unix socket** partilhado.
- Resultado: **existe um só engine**. Os containers, as images, os volumes e as networks são os mesmos,
  quer use `docker` no Ubuntu ou `docker` no PowerShell.

---

## 2. Arquitetura

```
┌──────────────────────────── Windows 11 Pro (host) ────────────────────────────┐
│                                                                               │
│  Docker Desktop 4.82.0 (GUI + backend)          PowerShell                     │
│        │                                         docker.exe ──┐               │
│        │ gere                                                 │ named pipe    │
│        ▼                                                      ▼               │
│  ┌────────────── WSL 2 (VM leve, kernel 6.18.33.2) ─────────────────────────┐  │
│  │                                                                         │  │
│  │  distro: docker-desktop                  distro: Ubuntu 26.04 LTS       │  │
│  │  ┌──────────────────────────┐            ┌───────────────────────────┐  │  │
│  │  │ dockerd 29.6.1  (engine) │◀── Unix ───│ docker CLI 29.6.1         │  │  │
│  │  │ containerd v2.2.5        │   socket   │ (symlink p/ cli-tools)    │  │  │
│  │  │ runc 1.3.6               │            │ docker compose v5.3.0     │  │  │
│  │  │ /var/lib/docker          │            │ docker buildx v0.35.0     │  │  │
│  │  └──────────────────────────┘            └───────────────────────────┘  │  │
│  │              ▲  partilhado via /mnt/wsl/docker-desktop                   │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────────────────┘
```

Todas as distros WSL 2 partilham **a mesma VM e o mesmo kernel**. Isso permite ao Docker
Desktop expor o engine ao Ubuntu sem rede: um diretório montado em `/mnt/wsl` é visível
em todas as distros.

---

## 3. Componentes

### 3.1 WSL

| Item | Valor |
|---|---|
| WSL version | 2.7.10.0 |
| Kernel | `6.18.33.2-microsoft-standard-WSL2` |
| Distros | `Ubuntu` (default, WSL 2) · `docker-desktop` (WSL 2) |
| `.wslconfig` | não existe — o WSL usa os defaults (~50% da RAM do host) |
| Host RAM | 15.7 GB → engine vê **~8 GB** e **20 CPUs** |

`/etc/wsl.conf` do Ubuntu:

```ini
[boot]
systemd=true

[user]
default=carlos_cabenda
```

> O `systemd` está ligado, mas isso **não** significa que exista um Docker nativo.
> O `systemctl is-active docker` dá `inactive`, e é assim que deve ficar.

### 3.2 Docker Desktop (Windows)

| Setting (`%APPDATA%\Docker\settings-store.json`) | Valor | Significado |
|---|---|---|
| `EnableIntegrationWithDefaultWslDistro` | `true` | integração ativa na distro default |
| `IntegratedWslDistros` | `["Ubuntu"]` | o Ubuntu recebe o CLI e o socket |
| `UseResourceSaver` | `false` | ✅ o engine não adormece (evita o problema da secção 5 do MEU-SETUP) |
| `AutoStart` | `false` | o Docker Desktop **não** arranca com o Windows — abrir à mão antes dos labs |
| `RunWinServiceInWslMode` | `true` | backend WSL 2 (não Hyper-V) |

- Versão: **Docker Desktop 4.82.0 (233772)**
- Kubernetes do Docker Desktop: **desligado** (o `kubectl` existe no Ubuntu, mas sem `current-context`)

### 3.3 Engine (servidor) — distro `docker-desktop`

| Item | Valor |
|---|---|
| Engine | 29.6.1 (API 1.55) |
| containerd | v2.2.5 |
| runc | 1.3.6 |
| Storage driver | `overlayfs` |
| Cgroup | `cgroupfs`, **cgroup v2** |
| Docker root dir | `/var/lib/docker` (dentro do disco do Docker Desktop, não do Ubuntu) |

### 3.4 Client — Ubuntu

| Item | Valor |
|---|---|
| Docker CLI | 29.6.1, `linux/amd64` |
| Compose | v5.3.0 (plugin) |
| Buildx | v0.35.0-desktop.2 |
| `docker context` ativo | `default` → `unix:///var/run/docker.sock` |
| Grupo `docker` | ✅ `carlos_cabenda` pertence a `docker` (gid 1001), por isso dispensa `sudo` |

---

## 4. Como o Ubuntu se liga ao engine

Tudo isto é **criado pelo Docker Desktop** quando ativa a integração. Eu não instalei nada.

### 4.1 O binário `docker`

```
/usr/bin/docker -> /mnt/wsl/docker-desktop/cli-tools/usr/bin/docker
```

O CLI não é um pacote do Ubuntu: é um **symlink** para o diretório partilhado
`/mnt/wsl/docker-desktop/`, que contém:

| Diretório | Função |
|---|---|
| `cli-tools/` | binários Linux do CLI (`docker`, plugins `compose`/`buildx`) |
| `shared-sockets/` | sockets do engine expostos às distros |
| `docker-desktop-user-distro` | agent que mantém a integração dentro do Ubuntu |

Se o Docker Desktop parar, este mount desaparece e o symlink fica **dangling**. Daí o erro
enganador `The command 'docker' could not be found in this WSL 2 distro` (ver MEU-SETUP §5).

### 4.2 O socket

```
/var/run/docker.sock  →  /run/docker.sock   srw-rw---- root:docker
```

O CLI usa o **context** `default`, que aponta para este socket. Como o grupo do socket é
`docker` e eu pertenço a esse grupo, não preciso de `sudo`.

### 4.3 Os binários do Windows também estão acessíveis

O Docker Desktop injeta ainda `/Docker/host/bin/` no Ubuntu, com os `.exe` do Windows:

```
docker.exe   docker-compose.exe   docker-credential-desktop.exe
docker-credential-wincred.exe   docker-credential-ecr-login.exe
```

O `which -a docker` mostra três candidatos, por ordem de prioridade no `PATH`:

```
/usr/bin/docker          ← o que é usado (CLI Linux via integração)
/bin/docker              ← mesmo ficheiro (/bin é symlink para /usr/bin)
/Docker/host/bin/docker  ← wrapper para o docker.exe do Windows (fallback)
```

O `docker.exe` fala com o engine pelo **named pipe** do Windows, não pelo socket. É por isso que
`docker.exe ps` consegue "acordar" o engine quando a integração cai.

### 4.4 Credentials

`~/.docker/config.json` no Ubuntu:

```json
{ "credsStore": "desktop.exe" }
```

Um `docker login` feito no Ubuntu **guarda as credentials no Windows Credential Manager**,
através do Docker Desktop. Login feito num lado vale para o outro.

---

## 5. Windows vs Ubuntu — o mesmo engine, endpoints diferentes

| | PowerShell (Windows) | Ubuntu (WSL) |
|---|---|---|
| Binário | `C:\Program Files\Docker\Docker\resources\bin\docker.exe` | `/usr/bin/docker` (Linux) |
| Context ativo | `desktop-linux` | `default` |
| Endpoint | `npipe:////./pipe/dockerDesktopLinuxEngine` | `unix:///var/run/docker.sock` |
| Engine | **o mesmo `dockerd` na distro `docker-desktop`** | ← |

Prova: `docker ps -a` e `docker images` dão o mesmo resultado nos dois lados.

> No Windows também existe o context `default` → `npipe:////./pipe/docker_engine`. Esse pipe
> é para **Windows containers** e não está em uso. Não mudar para ele.

---

## 6. Onde ficam os dados em disco

| O quê | Ficheiro no Windows | Tamanho (2026-11-18) |
|---|---|---|
| **Images, containers, volumes, build cache** | `%LOCALAPPDATA%\Docker\wsl\disk\docker_data.vhdx` | 3.21 GB |
| Sistema da distro `docker-desktop` | `%LOCALAPPDATA%\Docker\wsl\main\ext4.vhdx` | 0.09 GB |
| Distro Ubuntu (a minha home, `~/devops_automation`) | `%LOCALAPPDATA%\wsl\{c1a87a41-...}\ext4.vhdx` | — |

Consequências práticas:

- Apagar ou reinstalar o Ubuntu **não apaga** as images e os containers, que vivem no disco do Docker Desktop.
- Um **reset/uninstall do Docker Desktop apaga tudo** o que está no `docker_data.vhdx`.
- Os `.vhdx` crescem mas **não encolhem sozinhos**. Para libertar espaço:
  `docker system prune -a` e depois *Troubleshoot → Clean / Purge data*, ou compactar o vhdx.

### Estado atual do engine

| | Quantidade |
|---|---|
| Images | 5 — `nginx:alpine`, `alpine:latest`, `hashicorp/vault:latest`, `postgres:16`, `hello-world` |
| Containers | 5 (0 running) |
| Volumes | 4 |
| Networks custom | `sample-store-db_default`, `simbu_default`, `vault_network` (criadas pelo Compose) |

---

## 7. Bind mounts e performance

| Origem do bind mount | Caminho | Performance |
|---|---|---|
| Filesystem do Ubuntu | `~/devops_automation` | ✅ rápida — ficheiros nativos ext4 |
| Disco do Windows | `/mnt/c/Users/...` | ⚠️ lenta — atravessa o protocolo 9P |

Regra: correr os `docker compose up` a partir do **clone no WSL** (`~/devops_automation`),
nunca do clone em `/mnt/c/...`.

---

## 8. Checklist de arranque dos labs

```bash
# 0. Abrir o Docker Desktop no Windows (AutoStart está desligado)

# 1. No Ubuntu
wsl --cd ~/devops_automation          # (a partir do PowerShell)

docker version                         # Client e Server têm de aparecer
docker context show                    # deve dizer: default
docker run --rm hello-world            # teste end-to-end
```

| Sintoma | Causa provável | Ação |
|---|---|---|
| `docker: command not found in this WSL 2 distro` | Docker Desktop fechado ou engine parado | abrir o Docker Desktop; `docker.exe ps` para acordar |
| `Cannot connect to the Docker daemon` | engine ainda a arrancar | esperar 10–20 s |
| `permission denied ... docker.sock` | user fora do grupo `docker` | `sudo usermod -aG docker $USER` e reabrir o shell |
| `docker version` só mostra o Client | engine em baixo | reiniciar o Docker Desktop (ver MEU-SETUP §5) |

---

## 9. O que **não** fazer

- ❌ `sudo apt install docker.io` / `docker-ce` no Ubuntu. Isso cria um **segundo engine**, que
  compete pelo `/var/run/docker.sock` com o Docker Desktop: images "desaparecem" e os containers
  ficam em engines diferentes.
- ❌ `sudo systemctl enable docker`. Não há serviço local, e assim deve continuar.
- ❌ Mudar o context do Windows para `default` (Windows containers).
- ❌ Editar o `settings-store.json` com o Docker Desktop aberto, porque é sobrescrito.
