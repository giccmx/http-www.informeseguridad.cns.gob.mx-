# 🇲🇽 Homicide Reports in Mexico - Daily ETL Automation

**EN | English**

This project automates the daily extraction, transformation, and loading (ETL) of homicide data in Mexico, directly from the official government website [informeseguridad.cns.gob.mx](http://www.informeseguridad.cns.gob.mx/). It uses a Python-based pipeline powered by **requests**, and **pdfplumber** to extract and process data from dynamically generated content and PDF files. 

## 🚀 Purpose

To provide structured, timely, and accessible data on daily homicides in Mexico for analysis, transparency, and public awareness.

## 🔧 How It Works

- **Extract**: 
  - Downloads the daily homicide PDF reports using `requests`.
- **Transform**:
  - Uses `pdfplumber` to parse and extract tables from PDF files.
  - Converts the extracted data into structured tabular format (Pandas DataFrame).
- **Load**:
  - Saves the final dataset locally (e.g., CSV or Parquet) or insert into a database.
  - Optional: You can modify to send the data to cloud storage or a database.

## 🛠️ Technologies

- Python 3.11
- requests
- pdfplumber
- Pandas
- GitHub Actions

## 📅 Automation

The entire pipeline is triggered daily using a scheduled GitHub Actions workflow (`cron` job). This ensures the dataset stays continuously updated.

## 📁 Output

The resulting dataset is version-controlled and ready for:
- Data journalism
- Civic tech initiatives
- Academic research
- Government accountability tracking

## 📬 Contact & Social Media

Feel free to reach out or follow me for more data-driven civic tech tools:

✉️ Email: [abadejos.arenosa_8q@icloud.com]
💼 LinkedIn: [https://www.linkedin.com/in/giccmx]
🐦 Twitter/X: [https://x.com/giccmx]
🌐 Website: [https://gicc.mx]
🗞️ Newsletter: [https://gicc.mx/newsletter]
💵 Donations: [https://gicc.mx/Donations]
▶️ YouTube: [https://www.youtube.com/@giccmx]

---

**ES | Español**

Este proyecto automatiza diariamente la extracción, transformación y carga (ETL) de datos sobre homicidios en México, directamente desde el sitio oficial del gobierno [informeseguridad.cns.gob.mx](http://www.informeseguridad.cns.gob.mx/). El proceso usa **requests** y **pdfplumber** en Python para interactuar con el sitio web, descargar los reportes PDF y extraer tablas estructuradas. 

## 🚀 Propósito

Proveer datos estructurados, actualizados y accesibles sobre los homicidios diarios en México, fomentando el análisis, la transparencia y la conciencia pública.

## 🔧 ¿Cómo Funciona?

- **Extract (Extraer)**:
  - Descarga los reportes PDF diarios mediante `requests`.
- **Transform (Transformar)**:
  - Usa `pdfplumber` para extraer las tablas desde los archivos PDF.
  - Convierte los datos en un formato tabular estructurado (DataFrame de Pandas).
- **Load (Cargar)**:
  - Guarda los datos en CSV o Parquet o el set de datos está listo para cragar a cualquier base de datos.
  - (Opcional) Puedes modificar el script para cargar los datos en la nube o en una base de datos.

## 🛠️ Tecnologías

- Python 3.11
- requests
- pdfplumber
- Pandas
- GitHub Actions

## 📅 Automatización

El pipeline completo se ejecuta diariamente mediante un flujo de trabajo programado (`cron`) en GitHub Actions. Esto garantiza que los datos estén siempre actualizados.

## 📁 Salida

El dataset resultante queda controlado por versiones y puede usarse para:
- Periodismo de datos
- Proyectos de tecnología cívica
- Investigación académica
- Seguimiento a políticas públicas

---

## 🤝 Contribuciones

¿Tienes sugerencias o ideas para mejorar este proyecto? ¡Estás invitado a contribuir! Puedes abrir un *issue* o enviar un *pull request*.

---

> Proyecto con fines cívicos y de investigación. No está afiliado oficialmente a ninguna institución gubernamental.


## 📬 Contacto & Redes Sociales

No dudes en comunicarte conmigo o seguirme para obtener más herramientas de tecnología cívica basadas en datos:

✉️ Email: [abadejos.arenosa_8q@icloud.com]
💼 LinkedIn: [https://www.linkedin.com/in/giccmx]
🐦 Twitter/X: [https://x.com/giccmx]
🌐 Website: [https://gicc.mx]
🗞️ Newsletter: [https://gicc.mx/newsletter]
💵 Donations: [https://gicc.mx/Donations]
▶️ YouTube: [https://www.youtube.com/@giccmx]