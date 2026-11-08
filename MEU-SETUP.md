# Meu Setup — DevOps Automation (fork de estudo)

Notas pessoais do meu ambiente. **Não vêm do curso** — são as adaptações necessárias
para a minha máquina. O guia oficial é `00-intro/README.md`.

Criado em 2026-11-08.

---

## 1. O meu ambiente

| Item | Valor |
|---|---|
| Host | Windows 11 Pro (26200) |
| Distro WSL | Ubuntu **26.04 LTS** — codename `resolute` |
| Arquitetura | `x86_64` (Intel/AMD) |
| Clone de trabalho | `~/devops_automation` (dentro do WSL) |
| Clone secundário | `C:\Users\Carlos Cabenda\Documents\MyReposDev\DevOps\devops_automation` |

**Os labs correm no WSL**, não no Windows. Os comandos do curso são todos Linux/apt,
e o filesystem nativo do WSL é muito mais rápido que `/mnt/c`.

```powershell
wsl --cd ~/devops_automation
```

> ⚠️ Os dois clones são cópias independentes do mesmo fork. Commit num lado exige
> `git pull` no outro.

### PowerShell vs WSL — dois mundos, nunca os dois ao mesmo tempo

**Não existe "PowerShell com o WSL ativado".** O comando `wsl` não ativa nada no
PowerShell — ele **troca-me** de shell. Estou sempre num mundo ou no outro.

| | PowerShell | Dentro do WSL |
|---|---|---|
| Prompt | `PS C:\Users\...>` | `carlos_cabenda@DESKTOP-NDE0RBK:~$` |
| Shell | PowerShell | bash (Linux) |
| `apt`, `apt install` | ❌ não existe | ✅ |
| Comandos do curso | ❌ não correm | ✅ correm tal e qual |
| Sair | — | `exit` volta ao PowerShell |

Regra prática: **olhar para o prompt**. Se vejo `PS` e uma letra de drive, estou no
Windows e os comandos do curso não funcionam. Se vejo `carlos_cabenda@...$`, estou no
Linux e posso colar tudo.

#### Armadilha 1: o `sudo` existe no PowerShell

O Windows 11 tem o seu próprio `sudo.exe`, que **não** é o `sudo` do Linux. Se colar
`sudo apt install -y unzip` no PowerShell por engano, não recebo um limpo "comando não
encontrado" — o Windows corre o `sudo` dele e dá um erro confuso sobre o `apt`. É o tipo
de erro que faz perder meia hora a pensar que o WSL está mal configurado.

#### Armadilha 2: `wsl` não aterra na home

Escrever `wsl` estando numa pasta do Windows aterra no **caminho traduzido**, não na home:

```
pasta no Windows:  C:\Users\Carlos Cabenda\Documents\MyReposDev\DevOps\devops_automation
pwd dentro do WSL: /mnt/c/Users/Carlos Cabenda/Documents/MyReposDev/DevOps/devops_automation
```

Isso põe-me no **clone errado** (o do Windows) e no filesystem lento. Por isso entro
sempre com o caminho explícito:

```powershell
wsl --cd ~/devops_automation    # aterra em /home/carlos_cabenda/devops_automation
wsl --cd ~                      # aterra em /home/carlos_cabenda
```

Alternativa mais confortável: abrir o **Windows Terminal** e escolher o perfil **Ubuntu**
no dropdown — nem passo pelo PowerShell, abre já em bash na minha home.

---

## 2. Git: fork e remotes

Fork: <https://github.com/josecarloscabenda/devops_automation>
(fork de `iesodias/devops_automation`, repo de labs do curso)

| Remote | Aponta para | Uso |
|---|---|---|
| `origin` | `josecarloscabenda/devops_automation` | o meu fork — push livre |
| `upstream` | `iesodias/devops_automation` | repo do instrutor — **só fetch** |

O push url do `upstream` está deliberadamente a `DISABLED`, para nunca enviar os meus
testes para o repo do curso por acidente. **Isto não é um bug — não "corrigir".**

```bash
# verificar
git remote -v        # upstream deve mostrar: DISABLED (push)
```

### Trazer atualizações do instrutor

O instrutor continua a commitar no repo do curso:

```bash
git fetch upstream
git merge upstream/main
git push origin main
```

### Se algo correr mal num lab e quiser voltar ao estado do curso

```bash
git checkout -- .                      # descartar alterações não commitadas
git reset --hard upstream/main          # voltar ao estado exato do instrutor (destrutivo)
```

---

## 3. Mapa de dependências por módulo

Instalo **à medida que chego a cada módulo**, não tudo de uma vez.

| Módulo | Precisa de | Estado inicial |
|---|---|---|
| 00, 01 — intro, git/linux/vi | git, vi, coreutils | ✅ já tenho |
| 02 — Docker | integração WSL do Docker Desktop | ✅ ativo e validado |
| 03 — Cloud AWS/Azure | aws cli, az cli (+ `unzip`) | ❌ instalar |
| 04 — Terraform | terraform (+ `gnupg`) | ❌ instalar |
| 05 — Automação CLI | aws/az cli + `jq` | ❌ instalar |
| 06 — Ansible | ansible — **só funciona em WSL** | ❌ instalar |
| 07 — GitHub Actions | nada local | ✅ fork pronto |
| 08 — Kubernetes | kubectl, helm, cluster | ❌ instalar |
| 09 — Datadog | conta Datadog + cluster/EC2 | ❌ depende de 03/08 |
| 10 — IA DevOps | API key (Gemini) | ❌ só credencial |
| 11 — Python DevOps | `python3-pip` | ⚠️ `venv` ok, falta pip |
| 12 — FinOps | recursos cloud ativos | ❌ depende de 03/08 |

---

## 4. Comandos corrigidos para o meu ambiente

> O `sudo` pede password no meu WSL — estes comandos têm de ser corridos
> interativamente por mim.

### 4.1 Base comum (antes do módulo 03 ou 04)

`unzip` e `gnupg` **não vêm instalados** e são pré-requisitos escondidos: sem `unzip`
o AWS CLI não descompacta, sem `gnupg` a chave GPG do Terraform falha.

```bash
sudo apt update && sudo apt install -y unzip gnupg jq
```

`watch` **já está instalado** — o passo 9 do guia do curso é desnecessário para mim.

### 4.2 Terraform (módulo 04)

Diferença vs. o curso: a suite é `resolute`, não `noble` (o curso hardcoda `noble`).
Ambas existem no repo da HashiCorp, mas a correta para Ubuntu 26.04 é `resolute`.

```bash
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg

echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com resolute main" | sudo tee /etc/apt/sources.list.d/hashicorp.list

sudo apt update && sudo apt install terraform -y
terraform -version
```

### 4.3 AWS CLI (módulo 03)

Sempre a variante **x86_64**, nunca ARM64.

```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
aws --version
```

### 4.4 Azure CLI (módulo 03)

Igual ao curso.

```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
az version
```

### 4.5 Ansible (módulo 06)

```bash
sudo apt install ansible -y
ansible --version
```

**Porque é que isto obriga a WSL:** a Red Hat não suporta Windows como *control node*
do Ansible — só como máquina gerida. É a única ferramenta do curso sem alternativa
nativa em Windows. As outras (aws cli, az cli, terraform, kubectl) têm instalador
Windows e estão disponíveis via `winget`, mas uso WSL para ter um ambiente único,
igual ao do instrutor.

### 4.6 kubectl (módulo 08)

Já tenho kubectl no **Windows** (v1.36.1), mas preciso dele dentro do **WSL**.
Variante `linux/amd64`.

```bash
KUBECTL_VERSION=$(curl -Ls https://dl.k8s.io/release/stable.txt)
curl -LO "https://dl.k8s.io/release/$KUBECTL_VERSION/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
kubectl version --client
```

### 4.7 Python (módulo 11)

O `pip` não vem no Ubuntu (o `venv` já está disponível).

```bash
sudo apt install -y python3-pip python3-venv
```

---

## 5. Docker no WSL — ✅ resolvido (2026-11-08)

Integração WSL do Docker Desktop ativa para a distro `Ubuntu`. Validado:
client **29.6.1** ↔ server **29.6.1** (linux/amd64), Compose **v5.3.0**, buildx **v0.35.0**,
`hello-world`, build de imagem, bind mount do repo, porta publicada e `compose up`
com `curl` a responder 200. O módulo 02 está desbloqueado.

```bash
# validação rápida
docker version
docker run --rm hello-world
```

### ⚠️ Resource Saver — isto vai voltar a acontecer

**O caso mais provável de o docker "deixar de funcionar" no WSL.** Aconteceu-me no mesmo
dia, 2h depois de validar tudo.

O Resource Saver do Docker Desktop (**ligado por omissão**) adormece o motor Linux após
~10 min sem uso. Ao adormecer, **desmonta a integração do Ubuntu** — no log:
`engine linux/wsl stopping hypervisor process` seguido de
`cleaning up agent for distro Ubuntu`. O `/mnt/wsl/docker-desktop` desaparece e o
`/usr/bin/docker` fica um symlink pendurado.

O comando então cai no shim do Windows, que imprime:

```
The command 'docker' could not be found in this WSL 2 distro.
We recommend to activate the WSL integration in Docker Desktop settings.
```

**Esta mensagem é enganadora** — a integração *está* ligada. O erro não tem nada a ver
com configuração. Não voltar a mexer no toggle por causa disto.

#### Como distinguir, em 1 comando

| `docker ps` no Windows | `docker ps` no WSL | Causa | Ação |
|---|---|---|---|
| ✅ funciona | ❌ falha | motor adormecido, integração desmontada | acordar o motor |
| ❌ erro 500 | ❌ falha | motor em baixo | reiniciar Docker Desktop |

#### Acordar o motor sem sair do WSL

```bash
docker.exe ps        # fala com a API do Windows e dispara o resume
# esperar ~10-20s
docker run hello-world
```

O `docker.exe` é alcançável de dentro do Ubuntu (em `/Docker/host/bin/docker.exe`,
injetado pelo Docker Desktop). A integração **reconstrói-se sozinha** quando o motor
volta — symlink e socket são recriados, sem precisar de tocar em settings.

#### Correção durável

**Docker Desktop → Settings → Resources → secção *Resource Saver*** (em algumas versões
dentro de *Advanced*) → desligar. Tem de ser na GUI: ao contrário das chaves da integração
WSL, o nome da chave do Resource Saver não aparece nos logs, por isso não vale a pena
adivinhar no `settings-store.json`.

Se preferir manter ligado (poupa RAM e bateria), o hábito é correr `docker.exe ps` antes
de começar os labs.

### Se voltar a falhar: como diagnosticar

Sintoma: `docker` aparece no `PATH` do Ubuntu (herdado do Windows) mas ao executar dá
`The command 'docker' could not be found in this WSL 2 distro.`

Ordem de diagnóstico — **não assumir que é a integração**, porque o sintoma é o mesmo
quando o motor está em baixo:

1. **O motor Linux está vivo?** No Windows: `docker version`. Se der
   `500 Internal Server Error` no pipe `dockerDesktopLinuxEngine`, o motor está em baixo —
   a integração não é o problema.
2. **A distro `docker-desktop` está a correr?** `wsl --list --verbose`. Com o motor WSL2
   saudável tem de estar `Running`. Se estiver `Stopped` com o Docker Desktop aberto,
   o motor não subiu.
3. **Logs do motor:** `%LOCALAPPDATA%\Docker\log\vm\init.log` — procurar
   `dockerd exited due to explicit Stop() call` e `VM is ready to be powered off`.
4. **Estado real da integração:** `%LOCALAPPDATA%\Docker\log\host\com.docker.backend.exe.log`,
   procurar `wslintegration`. A linha mostra o estado verdadeiro, ex.:
   `EnableIntegrationWithDefaultWslDistro:false, IntegratedWslDistros:[]string{}`.
5. **Artefactos dentro da distro** (existem só se a integração foi provisionada):
   `/usr/bin/docker` (symlink para `/mnt/wsl/docker-desktop/cli-tools/usr/bin/docker`),
   `/var/run/docker.sock`, e o user no grupo `docker`.

### Armadilha do primeiro dia: Apply & Restart preso

Cliquei em **Apply & Restart** e o Docker Desktop parou o motor mas **nunca o voltou a
ligar** — ficou preso a meio do restart. Resultado: a definição da integração nunca foi
gravada, mas a GUI dava a impressão de que tinha sido aplicada. Correção: matar os
processos do Docker Desktop, `wsl --shutdown`, relançar, e só depois aplicar a integração.

### Aplicar a integração sem a GUI

As definições vivem em `%APPDATA%\Docker\settings-store.json`. **Com o Docker Desktop
fechado** (senão é sobrescrito), as chaves são:

```json
{
  "EnableIntegrationWithDefaultWslDistro": true,
  "IntegratedWslDistros": ["Ubuntu"]
}
```

Fazer backup do ficheiro antes de editar. Depois arrancar o Docker Desktop e validar.

---

## 6. Módulo 07 — GitHub Actions no fork

O repo do curso **não traz nenhum workflow** — o módulo 07 é só README, os pipelines
são construídos por mim. Crio-os em `.github/workflows/`.

O GitHub Actions **já está ativo no meu fork** (`enabled: true`), portanto não há nada
a desbloquear: os workflows correm assim que fizer push.

---

## 7. ⚠️ Módulos que custam dinheiro

Os módulos **03, 04, 05, 09 e 12** criam recursos reais em AWS/Azure e **geram custos
na minha conta**. "Testar à vontade" nestes tem preço, ao contrário dos de Docker,
Git e Linux.

Hábitos a manter:

- `terraform destroy` no fim de cada lab de IaC
- verificar o billing/cost explorer depois de cada sessão
- no módulo 08, usar cluster local (Kubernetes do Docker Desktop ou `kind`) em vez de
  AKS/EKS sempre que o lab o permitir
- não deixar EC2/VMs ligadas de um dia para o outro
