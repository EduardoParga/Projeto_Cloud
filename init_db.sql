-- Schema para Azure SQL Database conforme especificação do projeto
CREATE TABLE Cotacoes (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    Ativo VARCHAR(10),
    DataPregao DATE,
    Abertura DECIMAL(10,2),
    Fechamento DECIMAL(10,2),
    Volume DECIMAL(18,2)
);

-- Adicionar índices para performance
CREATE INDEX IX_Cotacoes_Ativo ON Cotacoes(Ativo);
CREATE INDEX IX_Cotacoes_Data ON Cotacoes(DataPregao);