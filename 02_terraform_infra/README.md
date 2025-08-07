# IaC para MLOps con Terraform

## **Descripción General**

Este código de Terraform despliega la infraestructura base necesaria en Google Cloud Platform (GCP) para soportar pipelines de Machine Learning. Los recursos creados son:

* **Google Cloud Storage (GCS) Bucket**: Para almacenar datos, artefactos de modelos y otros archivos.
* **BigQuery Dataset**: Para almacenar datos estructurados, logs o resultados.
* **Cuenta de Servicio (IAM)**: Una identidad dedicada con los permisos mínimos necesarios para que Vertex AI pueda ejecutar los pipelines.
* **APIs de GCP**: Habilita todas las APIs requeridas (`Vertex AI`, `Storage`, `BigQuery`, etc.).

## **Requisitos Previos**

1.  **Google Cloud SDK (`gcloud`)**: [Instalado](https://cloud.google.com/sdk/docs/install) y autenticado.
    ```bash
    gcloud auth application-default login
    ```
2.  **Terraform**: [Instalado](https://learn.hashicorp.com/tutorials/terraform/install-cli) en tu máquina local (versión 1.0.0 o superior).

## **Estructura de Archivos**

```
.
├── main.tf         # Definición principal de los recursos.
├── variables.tf    # Variables de entrada.
├── outputs.tf      # Valores de salida del despliegue.
└── README.md       # Este archivo.
```

## **Instrucciones de Despliegue**

### **Paso 1: Configurar las Variables**

1.  Renombra el archivo `variables.tf.example` a `terraform.tfvars` (este archivo no se debe subir a Git).

2.  Edita el archivo `terraform.tfvars` con tus propios valores.

    ```hcl
    # terraform.tfvars

    project_id    = "tu-proyecto-gcp-aqui"
    bucket_name   = "nombre-de-bucket-unico-global-aqui"
    region        = "us-central1"
    # Puedes añadir otras variables aquí para sobreescribir los defaults.
    ```

### **Paso 2: Inicializar y Desplegar**

1.  Abre una terminal en la carpeta `02_terraform_infra/`.

2.  Inicializa Terraform. Esto descarga el proveedor de Google y prepara el entorno.
    ```bash
    terraform init
    ```

3.  (Opcional) Genera un plan de ejecución para ver qué cambios se aplicarán.
    ```bash
    terraform plan -var-file="terraform.tfvars"
    ```

4.  Aplica los cambios para crear la infraestructura. Deberás confirmar la acción escribiendo `yes`.
    ```bash
    terraform apply -var-file="terraform.tfvars"
    ```

Al finalizar, Terraform mostrará los valores definidos en `outputs.tf`, como el nombre del bucket y el email de la cuenta de servicio.

## **Limpieza**

Para destruir todos los recursos creados por este proyecto y evitar costos, ejecuta el siguiente comando:
```bash
terraform destroy -var-file="terraform.tfvars"
```