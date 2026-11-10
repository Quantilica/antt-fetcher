# Agência Nacional de Transportes Terrestres — dados abertos (`antt`)

O `antt-fetcher` coleta do portal de dados abertos da ANTT (`dados.antt.gov.br`, um CKAN) os arquivos CSV, JSON e XLSX de pacotes sobre rodovias concedidas, transporte de cargas, passageiros e ferrovias, e converte doze conjuntos para o lake em Parquet particionado por `ano`. O catálogo do fetcher cobre 106 pacotes do portal; os doze abaixo são os que o conversor sabe transformar.

| Dataset | O que é | Pacote do portal | Período no bruto | Estado | Página |
|---|---|---|---|---|---|
| `volume-trafego-praca-pedagio` | Veículos por praça de pedágio, mês ou dia | `volume-trafego-praca-pedagio` | 2010 a 2022, 2024 a 2026 | convertido | [volume-trafego-praca-pedagio](datasets/volume-trafego-praca-pedagio.md) |
| `acidentes-rodovias` | Acidentes nas rodovias concedidas | `acidentes-rodovias` | 2015 a 2026 | convertido | [acidentes-rodovias](datasets/acidentes-rodovias.md) |
| `rntrc` | Cadastro de transportadores de cargas | `rntrc` | instantâneo de set/2026 | convertido | [rntrc](datasets/rntrc.md) |
| `monitriip-servico-regular-paradas` | Paradas das viagens do serviço regular de passageiros | `monitriip-servico-regular-paradas` | 2019-01 a 2020-11, 2021-04, 2024-12 | convertido | [monitriip-servico-regular-paradas](datasets/monitriip-servico-regular-paradas.md) |
| `relatorio-acompanhamento-acidentes-ferroviarios-raaf` | Acidentes ferroviários e índice por concessionária | `relatorio-de-acompanhamento-de-acidentes-ferroviarios-raaf` | 2004 em diante | convertido | [relatorio-acompanhamento-acidentes-ferroviarios-raaf](datasets/relatorio-acompanhamento-acidentes-ferroviarios-raaf.md) |
| `ciot` | CIOTs emitidos por origem, destino e carga | `ciot` | 2020 a 2026 (incompleto) | convertido | [ciot](datasets/ciot.md) |
| `vale-pedagio-obrigatorio` | Emissões mensais de Vale-Pedágio Obrigatório | `vale-pedagio-obrigatorio` | 2025-04 a 2026-10 | convertido | [vale-pedagio-obrigatorio](datasets/vale-pedagio-obrigatorio.md) |
| `investimentos` | Investimentos anuais das concessionárias | `investimentos` | 2010 a 2025 | convertido | [investimentos](datasets/investimentos.md) |
| `praca-de-pedagio` | Cadastro das praças de pedágio | `praca-de-pedagio` | instantâneo de 2026-11 | convertido | [praca-de-pedagio](datasets/praca-de-pedagio.md) |
| `quantidade-possiveis-infratores` | Possíveis infratores por excesso de velocidade nos radares | `quantidade-possiveis-infratores` | 2022 a 2026 | convertido | [quantidade-possiveis-infratores](datasets/quantidade-possiveis-infratores.md) |
| `volume-radar` | Tráfego nos radares de velocidade | `volume-radar` | 2022 a 2026 | convertido | [volume-radar](datasets/volume-radar.md) |
| `volume-sat` | Tráfego nos equipamentos de contagem veicular | `volume-sat` | 2024 a 2026 | convertido | [volume-sat](datasets/volume-sat.md) |

## Como a ANTT publica

- O portal organiza um pacote por assunto, e cada pacote tem um recurso por arquivo: por concessionária (acidentes, radares, SAT), por mês (RNTRC, CIOT, Monitriip) ou por ano (volume de tráfego nas praças). Os pacotes trazem sempre o dicionário de dados em PDF e, em geral, um painel gráfico; alguns repetem os dados em JSON.
- Todos os pacotes conferidos declaram a licença Creative Commons Attribution (CC BY). O portal diz seguir a Política de Dados Abertos do Poder Executivo Federal (Decreto nº 8.777/2016). Não foi encontrada restrição de uso ou redistribuição além da atribuição.
- O portal fica atrás de um firewall que responde "Request Rejected" a acessos automatizados em excesso; o fetcher trata a resposta como falha transitória.
- Os dados de rodovias vêm das concessionárias (via Sistema de Informação de Rodovias, SIR) e cada concessionária tem estilo próprio: separador, codificação, cabeçalho e formato de data variam entre arquivos do mesmo pacote.

## O que vale para todos os datasets

- **Nome do arquivo no bruto.** `<pacote>_<recurso>-<id>@AAAAMMDD.csv`, em que o sufixo é a data da última modificação na fonte. Versões antigas do fetcher gravaram também `<pacote>@AAAAMMDD.csv` (nome nu), reaproveitado por recursos diferentes. O conversor não confia no nome: a versão vigente é escolhida por recurso, pela URL do manifesto ao lado. Versões do mesmo recurso se substituem (vale o carimbo mais novo), recursos diferentes coexistem (os meses do RNTRC, do CIOT e do Monitriip, as concessionárias e os anos), e o mesmo recurso sob dois nomes no mesmo carimbo entra uma vez só (o de nome com chave). O Parquet de um arquivo de nome nu leva o sufixo `_<id8>` do recurso no nome. Arquivo de nome nu **sem manifesto** ao lado não tem recurso conhecido e segue a regra do nome (só o mais recente de cada nome); no bruto conferido há alguns, citados nas páginas.
- **Todas as colunas são texto.** O lake guarda tudo como texto, com nomes normalizados (minúsculas, sem acento), inclusive datas (`dd/mm/aaaa`, `mm/aaaa`, `aaaa-mm-dd`) e números com vírgula ou ponto decimal.
- **`ano` é partição**, calculado da data da linha; para fotografias (`rntrc`, `ciot`, `praca-de-pedagio`) vem do período no nome do arquivo ou do carimbo.
- **Arquivos diário e mensal consolidado coexistem** em `volume-trafego-praca-pedagio`, `volume-radar` e `volume-sat` e somam o mesmo tráfego duas vezes (conferido numericamente nas praças em 2024, no radar da CRT e da Via040 e no SAT). Esses três datasets têm a coluna `granularidade` (`dia` ou `mes`, pelo formato da data da linha): filtre uma só granularidade antes de somar.
- **Manifestos sem arquivo.** Na listagem do bruto conferida em 2026-11-10, 61 manifestos de arquivos baixados não têm o arquivo ao lado.
