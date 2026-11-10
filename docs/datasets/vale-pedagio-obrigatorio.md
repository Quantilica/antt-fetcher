---
dataset:
  id: "vale-pedagio-obrigatorio"
  fonte: "antt"
  titulo: "Vale-Pedágio Obrigatório (VPO)"
  resumo: "Emissões mensais de Vale-Pedágio Obrigatório agregadas por categoria do transportador e modelo."
  orgao: "Agência Nacional de Transportes Terrestres (ANTT)"
  pagina_oficial: "https://dados.antt.gov.br/dataset/vale-pedagio-obrigatorio"
  licenca: "Creative Commons Attribution (CC BY), conforme o conjunto no portal de dados abertos da ANTT: http://www.opendefinition.org/licenses/cc-by. Nenhuma restrição de uso ou redistribuição foi encontrada além da atribuição; o portal fica atrás de um firewall que rejeita acessos automatizados em excesso (respostas \"Request Rejected\"), o que limita a coleta."
  periodicidade: "mensal segundo o portal"
  cobertura: {inicio: "2025-04", fim: em-curso}
  unidade: "as emissões de VPO de um mês, uma categoria de transportador e um modelo"
  granularidade: {espacial: "nacional", temporal: "mês"}
  formato_bruto: "CSV único, Windows-1252, separador ponto e vírgula, sem aspas"
  lake: {estado: convertido, particoes: ["ano"], chave: ["ano", "ano_de_emissao", "mes_de_emissao", "categoria_do_transportador", "modelo_do_vpo"], colunas: 8}
  unidades_de_medida: {no_de_transportadores: "transportadores", no_de_veiculos: "veículos", no_de_vpos: "VPOs", valor_dos_vpos: "não informada pela fonte"}
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-10
  versao_fetcher: 0.3.2
---

# Vale-Pedágio Obrigatório (VPO)

## Resumo

Dados mensais das emissões de Vale-Pedágio Obrigatório (VPO), por categoria do transportador e modelo, da ANTT (Superintendência de Cargas). O pacote no portal não lista recursos e não publica dicionário; as descrições abaixo vêm só dos cabeçalhos do arquivo.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `antt/vale-pedagio-obrigatorio` |
| Órgão | Agência Nacional de Transportes Terrestres (ANTT) |
| Página oficial | https://dados.antt.gov.br/dataset/vale-pedagio-obrigatorio |
| Licença | Creative Commons Attribution (CC BY), conforme o conjunto no portal de dados abertos da ANTT: http://www.opendefinition.org/licenses/cc-by. Nenhuma restrição de uso ou redistribuição foi encontrada além da atribuição; o portal fica atrás de um firewall que rejeita acessos automatizados em excesso (respostas "Request Rejected"), o que limita a coleta. |
| Periodicidade | mensal segundo o portal |
| Cobertura | 2025-04 a em-curso |
| Unidade (uma linha) | as emissões de VPO de um mês, uma categoria de transportador e um modelo |
| Granularidade | espacial: nacional; temporal: mês |
| Formato bruto | CSV único, Windows-1252, separador ponto e vírgula, sem aspas |
| Estado no lake | convertido |
| Partições | `ano` |
| Chave | `ano`, `ano_de_emissao`, `mes_de_emissao`, `categoria_do_transportador`, `modelo_do_vpo` |
| Colunas | 8 |
| Unidades de medida | `no_de_transportadores`: transportadores; `no_de_veiculos`: veículos; `no_de_vpos`: VPOs; `valor_dos_vpos`: não informada pela fonte |
| Dados pessoais | nenhum |
| Eras | nenhuma |
| Revisado em | 2026-11-10 |
| Versão do fetcher | 0.3.2 |

## Origem e coleta

- O fetcher baixa um CSV único (`vpo-vale-pedagio-obrigatorio.csv`) do endereço registrado no pacote `vale-pedagio-obrigatorio` (`https://dados.antt.gov.br/dataset/vale-pedagio-obrigatorio`). O pacote exibe 0 recursos na API do portal em 2026-11-10; o arquivo existe no endereço de download.
- No bruto: `vale-pedagio-obrigatorio@AAAAMMDD.csv` (data da última modificação), com manifesto.

## Conteúdo

- Unidade de análise: o conjunto de emissões de um mês, uma categoria de transportador e um modelo (a combinação é única nas 75 linhas conferidas).
- Cobertura anunciada pela fonte: mensal. O que veio: abril de 2025 a outubro de 2026 (19 meses), **com outubro de 2026 parcial**, pois o arquivo é de 2026-10-06.
- Layout: 8 colunas; 75 linhas, que é o total de linhas do CSV menos o cabeçalho. Sem nulos.

## Variáveis

Cabeçalhos do CSV (sem dicionário da fonte): onde a coluna não é definida pela fonte, a descrição diz "sem dicionário publicado". Todos os valores chegam ao lake como texto. A coluna de partição `ano` não está nos arquivos.

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `ano_de_emissao` | `Ano de Emissão` | texto | Ano de emissão do Vale-Pedágio (cabeçalho da fonte; sem dicionário publicado) | ano de 4 dígitos | todo |
| `mes_de_emissao` | `Mês de Emissão` | texto | Mês de emissão (sem dicionário publicado) | 1 a 12, sem zero à esquerda | todo |
| `categoria_do_transportador` | `Categoria do Transportador` | texto | Categoria do transportador (sem dicionário publicado) | `ETC`, `CTC`, `TAC`, `Não Informado` (conferido) | todo |
| `modelo_do_vpo` | `Modelo do VPO` | texto | Modelo do Vale-Pedágio Obrigatório (sem dicionário publicado) | `Tag` (único valor conferido) | todo |
| `no_de_transportadores` | `Nº de Transportadores` | texto | Número de transportadores (sem dicionário publicado; o cabeçalho diz "Nº de Transportadores") | transportadores | todo |
| `no_de_veiculos` | `Nº de Veículos` | texto | Número de veículos (sem dicionário publicado) | veículos | todo |
| `no_de_vpos` | `Nº de VPOs` | texto | Número de Vales-Pedágio Obrigatórios (sem dicionário publicado) | VPOs | todo |
| `valor_dos_vpos` | `Valor dos VPOs` | texto | Valor dos VPOs (sem dicionário publicado). A fonte não informa a unidade; os valores têm ponto decimal e duas casas (`2083658.08`) | unidade não informada pela fonte | todo |

## No lake

- Dataset `antt/vale-pedagio-obrigatorio`, particionado por `ano` (de `ano_de_emissao`, partições 2025 e 2026), um Parquet por ano e arquivo (`vale-pedagio-obrigatorio_<id8>.parquet`, em que `<id8>` são os 8 primeiros caracteres do id do recurso na URL do manifesto).
- Todas as colunas são texto. Os nomes viram `ano_de_emissao`, `mes_de_emissao`, `no_de_transportadores`, `no_de_veiculos`, `no_de_vpos` e `valor_dos_vpos` (o símbolo "º" some na normalização).
- A coluna `ano_de_emissao` está nos dados e na partição `ano`.
- Esquema de referência (`vale-pedagio-obrigatorio.schema.json`): 8 colunas, gerado da conversão do arquivo inteiro.

## Cuidados de uso

- **Mês corrente parcial.** O último mês do arquivo (outubro de 2026) tem só os dias até a data de geração; não o compare com meses fechados.
- **Unidade do valor não informada.** A fonte não diz se `valor_dos_vpos` é a soma em reais; a leitura como reais não está confirmada.
- **`Não Informado`** aparece como categoria do transportador (mantido como texto).
- **O pacote está sem recursos na API.** Se o endereço de download mudar, o fetcher não o encontra pelo catálogo do portal.

## Exemplos

Valor total de VPOs por mês (unidade conforme a fonte, não confirmada):

```python
import polars as pl

v = pl.scan_parquet("lake/antt/vale-pedagio-obrigatorio/ano=*/*.parquet")
mensal = (
    v.group_by("ano_de_emissao", "mes_de_emissao")
    .agg(pl.col("valor_dos_vpos").cast(pl.Float64).sum().alias("valor"))
    .sort(pl.col("ano_de_emissao").cast(pl.Int32), pl.col("mes_de_emissao").cast(pl.Int32))
    .collect()
)
```

## Referências

- Pacote: https://dados.antt.gov.br/dataset/vale-pedagio-obrigatorio
- Dicionário de dados: não publicado pela fonte
