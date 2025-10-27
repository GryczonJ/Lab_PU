CREATE TABLE [dbo].[Technika] (
    [Id]    INT          IDENTITY (1, 1) NOT NULL,
    [hasło] NCHAR (100)  NULL,
    [treść] NCHAR (2000) NULL,
    PRIMARY KEY CLUSTERED ([Id] ASC)
);