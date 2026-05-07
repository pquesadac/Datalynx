
#  sample_data.py — Datos de demo para Datalynx


SAMPLE_CVS = [
    {
        "id": 1,
        "nombre": "María García López",
        "email": "maria.garcia@email.com",
        "telefono": "612345678",
        "edad": 28,
        "texto_cv": """
        María García López, 28 años. Correo: maria.garcia@email.com | Tel: 612345678

        EXPERIENCIA PROFESIONAL
        Data Scientist — Telefónica (2021 - 2024)
        Desarrollo de modelos de machine learning para predicción de churn de clientes.
        Análisis de datos con Python y Pandas. Visualización con Power BI y Matplotlib.
        Despliegue de modelos en AWS SageMaker.

        Analista de Datos — BBVA (2020 - 2021)
        Generación de reportes de negocio en SQL y Excel. Transformación de datos con ETL.

        FORMACIÓN
        Grado en Ingeniería Informática — Universidad Complutense de Madrid (2020)
        Máster en Data Science — IE Business School (2021)

        HABILIDADES
        Python, Machine Learning, Scikit-Learn, TensorFlow, SQL, Pandas, NumPy,
        Power BI, AWS, Docker, estadística avanzada, inglés C1.
        """,
    },
    {
        "id": 2,
        "nombre": "Carlos Ruiz Martínez",
        "email": "carlos.ruiz@correo.es",
        "telefono": "699123456",
        "edad": 34,
        "texto_cv": """
        Carlos Ruiz Martínez, 34 años. Email: carlos.ruiz@correo.es | Móvil: 699123456

        EXPERIENCIA
        Senior Backend Developer — Inditex (2018 - 2024)
        Desarrollo de microservicios con Python y FastAPI. Gestión de bases de datos
        PostgreSQL y MongoDB. Despliegue en Kubernetes sobre AWS. 6 años de experiencia.

        Backend Developer — Mercadona Tech (2016 - 2018)
        APIs REST con Django. Integración con sistemas de terceros. SQL avanzado.

        ESTUDIOS
        Ingeniería de Telecomunicaciones — UPM (2015)

        HABILIDADES TÉCNICAS
        Python, FastAPI, Django, SQL, PostgreSQL, MongoDB, Docker, Kubernetes, AWS,
        Redis, RabbitMQ, Git, metodologías Agile/Scrum.
        """,
    },
    {
        "id": 3,
        "nombre": "Lucía Fernández Torres",
        "email": "lucia.ft@gmail.com",
        "telefono": "654987321",
        "edad": 25,
        "texto_cv": """
        Lucía Fernández Torres, 25 años. lucia.ft@gmail.com | 654987321

        EXPERIENCIA
        Junior Data Analyst — Accenture (2023 - 2024)
        Análisis exploratorio de datos con Python y Pandas. Dashboards en Tableau.
        Consultas SQL para extracción de datos. 1 año de experiencia.

        Prácticas en Análisis de Datos — Santander (2022 - 2023)
        Procesamiento de datos financieros. Informes en Excel y Power BI.

        FORMACIÓN
        Doble Grado: ADE + Estadística — Universidad de Sevilla (2022)
        Bootcamp Data Science — The Bridge (2023)

        HABILIDADES
        Python, Pandas, SQL, Tableau, Power BI, R, estadística, Excel avanzado, inglés B2.
        """,
    },
    {
        "id": 4,
        "nombre": "Andrés López Sánchez",
        "email": "andres.lopez@outlook.com",
        "telefono": "677234567",
        "edad": 31,
        "texto_cv": """
        Andrés López Sánchez, 31 años. andres.lopez@outlook.com | 677234567

        EXPERIENCIA LABORAL
        Machine Learning Engineer — Cabify (2020 - 2024)
        Diseño e implementación de modelos de Deep Learning con TensorFlow y PyTorch.
        NLP con spaCy y Transformers (BERT, GPT). Despliegue en GCP. 4 años de experiencia.

        Data Scientist — AECOM España (2019 - 2020)
        Modelos predictivos con Scikit-Learn. Análisis estadístico con R y Python.

        EDUCACIÓN
        Grado en Matemáticas — Universidad Autónoma de Madrid (2018)
        Máster en Inteligencia Artificial — UPM (2019)

        STACK TÉCNICO
        Python, TensorFlow, PyTorch, Scikit-Learn, spaCy, NLP, Transformers, BERT,
        GCP, Spark, SQL, Kubernetes, MLflow, inglés C2.
        """,
    },
    {
        "id": 5,
        "nombre": "Sara Navarro Pérez",
        "email": "sara.navarro@empresa.com",
        "telefono": "611876543",
        "edad": 29,
        "texto_cv": """
        Sara Navarro Pérez, 29 años. Contacto: sara.navarro@empresa.com | 611876543

        TRAYECTORIA PROFESIONAL
        Data Engineer — Glovo (2021 - 2024)
        Diseño de pipelines de datos con Apache Spark y Airflow. Gestión de data lakehouse
        en AWS S3 y Databricks. PostgreSQL, Kafka y Redis para arquitecturas en streaming.
        3 años de experiencia en entornos de alta carga.

        Analista BI — Ferrovial (2020 - 2021)
        Construcción de cubos OLAP. Dashboards de negocio con Power BI.

        FORMACIÓN
        Ingeniería Informática — Universidad Carlos III (2019)

        HABILIDADES
        Python, Spark, Airflow, Kafka, AWS, Databricks, SQL, PostgreSQL,
        Redis, Docker, Power BI, trabajo en equipo, inglés C1.
        """,
    },
    {
        "id": 6,
        "nombre": "Miguel Herrera Gómez",
        "email": "miguelh@yahoo.es",
        "telefono": "636451289",
        "edad": 42,
        "texto_cv": """
        Miguel Herrera Gómez, 42 años. miguelh@yahoo.es | 636451289

        EXPERIENCIA
        Técnico de RRHH — Manpower (2010 - 2018)
        Gestión de procesos de selección. Entrevistas y evaluación de candidatos.
        Uso de ATS como Personio y Workday. 8 años de experiencia en RRHH.

        Administrativo — Randstad (2008 - 2010)
        Gestión documental y base de datos de candidatos en Excel.

        FORMACIÓN
        Diplomatura en Relaciones Laborales — Universidad de Valladolid (2007)

        HABILIDADES
        Microsoft Office, Excel, Personio, Workday, comunicación, liderazgo,
        gestión de equipos, trabajo en equipo, español nativo.
        """,
    },
]

SAMPLE_JOBS = [
    {
        "id": 1,
        "titulo": "Data Scientist",
        "descripcion": """
        Buscamos un Data Scientist con experiencia en desarrollo de modelos de machine learning
        y análisis de datos. El candidato trabajará en proyectos de predicción y clasificación
        utilizando Python. Se valorará experiencia en entornos cloud y visualización de datos.
        Imprescindible experiencia con Scikit-Learn, Pandas y SQL. Deseable conocimiento de
        TensorFlow o PyTorch. Inglés nivel B2 mínimo. 2 años de experiencia mínima.
        """,
        "habilidades_requeridas": [
            "Python", "Machine Learning", "Scikit-Learn", "Pandas", "SQL",
            "estadística", "AWS", "Docker"
        ],
    },
    {
        "id": 2,
        "titulo": "Machine Learning Engineer",
        "descripcion": """
        Posición de ML Engineer para desarrollo e integración de modelos de inteligencia
        artificial en producción. Se requiere sólido conocimiento en NLP, Deep Learning
        y despliegue de modelos. Trabajarás con spaCy, TensorFlow o PyTorch y herramientas
        MLOps. Valorable experiencia con Transformers y BERT. Mínimo 3 años de experiencia.
        """,
        "habilidades_requeridas": [
            "Python", "TensorFlow", "PyTorch", "Scikit-Learn", "NLP", "spaCy",
            "Machine Learning", "Deep Learning", "AWS", "Docker", "SQL"
        ],
    },
    {
        "id": 3,
        "titulo": "Backend Developer Python",
        "descripcion": """
        Desarrollador backend con dominio de Python para construir APIs REST robustas
        y escalables. Conocimiento de FastAPI o Django. Experiencia con bases de datos
        relacionales (PostgreSQL, MySQL) y NoSQL (MongoDB, Redis). Despliegue con Docker
        y Kubernetes en cloud (AWS o GCP). Metodología Agile. Mínimo 3 años de experiencia.
        """,
        "habilidades_requeridas": [
            "Python", "FastAPI", "SQL", "PostgreSQL", "MongoDB", "Docker",
            "Kubernetes", "AWS", "Redis", "Git"
        ],
    },
]