# IoT Data Pipeline: EMQX -> Kafka -> MySQL

Ce projet configure un pipeline de données complet. Les messages MQTT envoyés à EMQX sont transférés vers Apache Kafka via Kafka Connect, puis persistés automatiquement dans une base de données MySQL.

---

## 1. Lancement de l'Infrastructure Docker

Démarrez l'ensemble des conteneurs (MySQL, Kafka, Kafka UI, EMQX, Kafka Connect) en arrière-plan :

```bash
docker compose up -d
```

> ⚠️ **Important** : Le conteneur MySQL s'initialise automatiquement avec la base de données et l'utilisateur requis. Kafka Connect télécharge et installe les plugins JDBC et MQTT au premier démarrage. Attendez environ 1 à 2 minutes avant de passer à l'étape suivante.

---

## 2. Configuration des Connecteurs Kafka Connect

Une fois Kafka Connect démarré (accessible sur le port `8084`), configurez les deux connecteurs en exécutant ces requêtes HTTP.

### Connecteur Source : EMQX vers Kafka
```bash
curl -X POST http://localhost:8084/connectors -H "Content-Type: application/json" -d '{
  "name": "emqx-to-kafka",
  "config": {
    "connector.class": "io.confluent.connect.mqtt.MqttSourceConnector",
    "tasks.max": "1",
    "mqtt.server.uri": "tcp://emqx:1883",
    "mqtt.topics": "capteurs/#",
    "kafka.topic": "topic-capteurs",
    "value.converter": "org.apache.kafka.connect.converters.ByteArrayConverter",
    "confluent.topic.bootstrap.servers": "kafka:29092",
    "confluent.topic.replication.factor": "1"
  }
}'
```

### Connecteur Sink : Kafka vers MySQL
```bash
curl -X POST http://localhost:8084/connectors -H "Content-Type: application/json" -d '{
  "name": "kafka-to-mysql",
  "config": {
    "connector.class": "io.confluent.connect.jdbc.JdbcSinkConnector",
    "tasks.max": "1",
    "topics": "topic-capteurs",
    "connection.url": "jdbc:mysql://mysql-local:3306/topic_capteurs",
    "connection.user": "mkc",
    "connection.password": "passer123",
    "insert.mode": "insert",
    "auto.create": "true",
    "auto.evolve": "true",
    "table.name.format": "capteurs",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "true",
    "key.converter": "org.apache.kafka.connect.storage.StringConverter"
  }
}'
```

### Vérification du Statut
Vérifiez que les deux connecteurs affichent bien le statut `RUNNING` :
```bash
curl -s http://localhost:8084/connectors/emqx-to-kafka/status | grep "RUNNING"
curl -s http://localhost:8084/connectors/kafka-to-mysql/status | grep "RUNNING"
```

---

## 3. Simulation des Données Capteurs

1. Créez l'environnement virtuel Python :
   ```bash
   # Sur Linux / macOS
   python3 -m venv env
   
   # Sur Windows
   python -m venv env
   ```

2. Activez l'environnement virtuel :
   ```bash
   # Sur Linux / macOS
   source env/bin/activate
   
   # Sur Windows (Command Prompt)
   env\Scripts\activate
   
   # Sur Windows (PowerShell)
   .\env\Scripts\Activate.ps1
   ```

3. Installez les dépendances requises :
   ```bash
   pip install -r requirements.txt
   ```

4. Lancez le script de simulation pour envoyer les messages MQTT en continu :
   ```bash
   python simulation.py
   ```
La table `capteurs` sera automatiquement créée dans MySQL lors de la réception du premier message et se remplira en temps réel.

---

## 4. Vérification de la Base de Données Docker

Pour valider le bon fonctionnement du pipeline et vous assurer que les données de la simulation sont correctement stockées, connectez-vous directement au conteneur MySQL.

1. Accédez au terminal interactif du conteneur MySQL :
   ```bash
   docker exec -it mysql-local mysql -u mkc -ppasser123 topic_capteurs
   ```

2. Vérifiez la présence de la table `capteurs` :
   ```sql
   SHOW TABLES;
   ```

3. Visualisez les valeurs insérées en temps réel par le pipeline :
   ```sql
   SELECT * FROM capteurs LIMIT 10;
   ```

4. Quittez l'interface MySQL :
   ```sql
   EXIT;
   ```
---

## 🎉 Félicitations !

Bravo ! Vous avez configuré avec succès le pipeline de données IoT EMQX-KAFKA.

### 🖥️ Accès aux Interfaces Graphiques

Vous pouvez piloter et surveiller votre infrastructure en temps réel via les outils d'administration visuels :

* **📊 Interface Graphique KAFKA (Kafka UI)** : [http://localhost:8080](http://localhost:8080)
* **🔌 Interface Graphique EMQX (Dashboard)** : [http://localhost:18083](http://localhost:18083)

Votre architecture valide désormais le parcours complet de la donnée, de la capture à la persistance en base de données.

