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

```bash
wsl -d Ubuntu
cd ~/devops_automation
```

> ⚠️ Os dois clones são cópias independentes do mesmo fork. Commit num lado exige
> `git pull` no outro.

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
| 02 — Docker | integração WSL do Docker Desktop | ⚠️ ver secção 5 |
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

## 5. Pendente: Docker no WSL

**A integração WSL do Docker Desktop está desligada para a distro Ubuntu.**

Sintoma: `docker` aparece no `PATH` do Ubuntu (herdado do Windows) mas ao executar dá:

```
The command 'docker' could not be found in this WSL 2 distro.
```

Não existe `/var/run/docker.sock` nem `/mnt/wsl/docker-desktop`.

**Como resolver** (GUI, antes do módulo 02):
Docker Desktop → Settings → Resources → WSL Integration → ativar `Ubuntu` → Apply & Restart

Validar:

```bash
docker version
docker run --rm hello-world
```

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
