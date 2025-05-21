# PySyncytium

## Définition & origine du projet

En biologie, Syncytium est un terme qui désigne une cellule qui est formée par la fusion de plusieurs cellules individuelles. Ce phénomène peut se produire dans divers contextes, notamment dans le développement embryonnaire, la formation de tissus musculaires et la réponse immunitaire.

En m'inspirant de ce terme, j'ai créé en 2016 un projet informatique visant à proposer un cadre technique (C#, HTML5 & Javascript ES 2016) capable de traiter un projet métier à partir de la description de son modèle de données. Ce projet visait à être en mesure de mettre à disposition une progressive web application (PWA) rapidement et simplement sans être attachée à une infrastructure imposée.

## Objectif

Ce projet vise à reprendre le principe, à le développer en Python et de fournir de nouvelles interfaces :
* WebSocket
* Web
* API
* ...

## Fonctionnalités

A partir d'une description JSON ou Yaml, ce cadre technique construit automatiquement des interfaces graphiques en mode Web, des accès API sécurisés et des fonctions accessibles via uns WebSocket :

```
Name: PSRoot
Description: "Gestion du périmètre de l'application PySyncytium'"
Version: 1

Tables:

  User:
    Name: User
    Description: "Liste des utilisateurs"
    Key:
      - Interface
      - Login
    Fields:
      Interface:
        Type: Integer
      Login:
        Description: "Identifiant"
        MaxLength: 80
      ClientId:
        Description: "Client"
        Type: Integer
      LastName:
        Description: "Nom de l'utilisateur"
        MaxLength: 40
      FirstName:
        Description: "Prénom de l'utilisateur"
        MaxLength: 40
      Password:
        Description: "Mot de passe"
        MaxLength: 128
      NewPassword:
        Description: "Clé pour changer de mot de passe"
        MaxLength: 128

  Client:
    Name: Client
    Description: "Liste des clients"
    Key: Id
    Fields:
      Id:
        Type: Integer
      Name:
        Description: "Nom du client"
        MaxLength: 40
        DefaultValue: "Concilium"

  Application:
    Name: Application
    Description: "Liste des applications"
    Key: Id
    Fields:
      Id:
        Type: Integer
      ClientId:
        Description: "Client"
        Type: Integer
      Name:
        Description: "Nom de l'application'"
        MaxLength: 40
        DefaultValue: "Test"
```

Le but, à termes, est d'offrir la possibilité de créer un service SaaS permettant de créer simplement des applications métiers : le tout en mode low-code, sans dépendance à une infrastructure imposée et ouvert aux outils d'IA.