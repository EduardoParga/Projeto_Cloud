# Documentação do Layout do Arquivo de Cotações Históricas da B3

Este documento descreve a estrutura e o layout dos arquivos de cotações históricas diárias (pregão) fornecidos pela B3. A especificação é baseada no documento `Catalogo_precos_v1.3.pdf`.

O arquivo é do tipo texto, com layout de posição fixa (fixed-width), onde cada linha representa um registro e cada campo ocupa uma posição e tamanho predefinidos.

## Estrutura Geral do Arquivo

O arquivo é composto por três tipos de registros, identificados pelo campo `TIPREG` (Tipo de Registro) na primeira coluna:

1.  **Registro 00 - Header:** A primeira linha do arquivo. Contém informações de identificação do arquivo, como nome, data de geração e data do pregão.
2.  **Registro 01 - Cotações:** O corpo do arquivo. Contém os dados das cotações de todos os instrumentos negociados no pregão. Cada linha representa a negociação de um papel em um determinado dia.
3.  **Registro 99 - Trailer:** A última linha do arquivo. Contém informações de fechamento, como o número total de registros no arquivo.

---

## Detalhamento dos Registros

A seguir, está o detalhamento dos campos para cada tipo de registro.

### Registro 00: Header

| Campo              | Posição (De-Até) | Tamanho | Formato     | Descrição                               |
| ------------------ | ---------------- | ------- | ----------- | --------------------------------------- |
| **TIPREG**         | 01-02            | 2       | Numérico    | **Fixo "00"** - Identificador do Header |
| **NOMEARQ**        | 03-15            | 13      | Alfanumérico| Nome do arquivo (ex: `COTAHIST.AAAA`)   |
| **CODORI**         | 16-23            | 8       | Alfanumérico| Código da origem (ex: `BOVESPA`)        |
| **DATGER**         | 24-31            | 8       | Numérico    | Data de geração do arquivo (AAAAMMDD)   |
| **DATPREG**        | 32-39            | 8       | Numérico    | Data do pregão (AAAAMMDD)               |
| **RESERV**         | 40-245           | 206     | Alfanumérico| Espaço reservado para uso futuro        |

### Registro 01: Cotações por Papel-Mercado

Este é o registro principal, contendo os dados de negociação.

| Campo              | Posição (De-Até) | Tamanho | Formato      | Descrição                                                              |
| ------------------ | ---------------- | ------- | ------------ | ---------------------------------------------------------------------- |
| **TIPREG**         | 01-02            | 2       | Numérico     | **Fixo "01"** - Identificador de Registro de Cotação                   |
| **DATPREG**        | 03-10            | 8       | Numérico     | Data do pregão (AAAAMMDD)                                              |
| **CODBDI**         | 11-12            | 2       | Alfanumérico | Código BDI (identificador do tipo de mercado)                          |
| **CODNEG**         | 13-24            | 12      | Alfanumérico | Código de negociação do papel (Ticker)                                 |
| **TPMERC**         | 25-27            | 3       | Numérico     | Tipo de mercado (ex: 010 para VISTA)                                   |
| **NOMRES**         | 28-39            | 12      | Alfanumérico | Nome resumido da empresa emissora do papel                             |
| **ESPECI**         | 40-49            | 10      | Alfanumérico | Especificação do papel (ex: ON, PN, PNA)                               |
| **PRAZOT**         | 50-52            | 3       | Alfanumérico | Prazo em dias do mercado a termo                                       |
| **MODREF**         | 53-56            | 4       | Alfanumérico | Moeda de referência (ex: `R$`)                                         |
| **PREABE**         | 57-69            | 13      | Numérico (9,2) | Preço de abertura do papel no dia                                      |
| **PREMAX**         | 70-82            | 13      | Numérico (9,2) | Preço máximo do papel no dia                                         |
| **PREMIN**         | 83-95            | 13      | Numérico (9,2) | Preço mínimo do papel no dia                                         |
| **PREMED**         | 96-108           | 13      | Numérico (9,2) | Preço médio do papel no dia                                          |
| **PREULT**         | 109-121          | 13      | Numérico (9,2) | Preço de fechamento do papel no dia                                    |
| **PREOFC**         | 122-134          | 13      | Numérico (9,2) | Preço da melhor oferta de compra                                       |
| **PREOFV**         | 135-147          | 13      | Numérico (9,2) | Preço da melhor oferta de venda                                        |
| **TOTNEG**         | 148-152          | 5       | Numérico     | Número de negócios efetuados com o papel                               |
| **QUATOT**         | 153-170          | 18      | Numérico     | Quantidade total de títulos negociados                                 |
| **VOLTOT**         | 171-188          | 18      | Numérico (16,2)| Volume total de títulos negociados                                     |
| **PREEXE**         | 189-201          | 13      | Numérico (9,2) | Preço de exercício para o mercado de opções                            |
| **DATVEN**         | 202-209          | 8       | Numérico     | Data do vencimento para os mercados de opções, futuro e termo          |
| **FATCOT**         | 210-216          | 7       | Numérico     | Fator de cotação do papel                                              |
| **PTOEXE**         | 217-229          | 13      | Numérico (6,7) | Preço de exercício em pontos para opções referenciadas em dólar        |
| **CODISI**         | 230-241          | 12      | Alfanumérico | Código ISIN do papel                                                   |
| **DISMES**         | 242-244          | 3       | Numérico     | Número de distribuição do papel                                        |

*Nota: Para campos numéricos com casas decimais, como `(9,2)`, significa que o campo tem um total de 13 dígitos, sendo 2 deles as casas decimais. O valor é representado sem o separador decimal.*

### Registro 99: Trailer

| Campo              | Posição (De-Até) | Tamanho | Formato     | Descrição                               |
| ------------------ | ---------------- | ------- | ----------- | --------------------------------------- |
| **TIPREG**         | 01-02            | 2       | Numérico    | **Fixo "99"** - Identificador do Trailer|
| **NOMEARQ**        | 03-15            | 13      | Alfanumérico| Nome do arquivo (o mesmo do header)     |
| **CODORI**         | 16-23            | 8       | Alfanumérico| Código da origem (o mesmo do header)    |
| **DATGER**         | 24-31            | 8       | Numérico    | Data de geração do arquivo (AAAAMMDD)   |
| **TOTREG**         | 32-42            | 11      | Numérico    | Número total de registros no arquivo (incluindo header e trailer) |
| **RESERV**         | 43-245           | 203     | Alfanumérico| Espaço reservado para uso futuro        |

---

Este documento serve como um guia rápido para o parsing e processamento dos dados. Para mais detalhes, consulte sempre a documentação oficial da B3.
