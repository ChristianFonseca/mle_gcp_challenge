# Flujo de Experimentación y Promoción

## **Descripción General**

Este proyecto implementa un flujo avanzado de MLOps usando MLFlow:

1.  **Experimentación**: Se ejecuta un "concurso" entre varios modelos (`LogisticRegression`, `RandomForest`, `XGBoost`) para encontrar el de mejor rendimiento para el dataset actual.
2.  **Registro del Campeón**: Solo el mejor modelo ("el campeón") del concurso es registrado en el **MLFlow Model Registry**.
3.  **Promoción Automatizada**: Un script desacoplado compara el campeón (en "Staging") con el modelo en "Production" y lo promueve si es superior.

## **Instrucciones de Ejecución**

### **Paso 1: Iniciar la UI de MLFlow**

En una terminal, dentro de esta carpeta, ejecuta:
```bash
mlflow ui
```
Accede a la interfaz en **`http://127.0.0.1:5000`**.

### **Paso 2: Ejecutar el Concurso de Modelos**

En una **nueva terminal**, ejecuta el siguiente comando para iniciar el proceso de experimentación.
```bash
mlflow run . -e experiment
```
Esto encontrará el mejor modelo y lo registrará. En la UI de MLFlow, verás un "Run Padre" con varios "Runs anidados" (uno por cada tipo de modelo probado). En la pestaña **Models**, verás una nueva versión del `churn-champion-model`.

### **Paso 3: Pasar el Modelo Campeón a "Staging"**

Ve a la UI de MLFlow, busca la última versión del `churn-champion-model` y transita su etapa a **Staging**. Este paso simula una validación humana o de negocio.

### **Paso 4: Ejecutar el Script de Promoción**

Ahora, decide si el nuevo campeón debe ir a producción.
```bash
mlflow run . -e promote
```
El script comparará las métricas `test_roc_auc` del modelo en `Staging` vs `Production` y actuará en consecuencia.

### **Paso 5: Verificar el Resultado**

Refresca la UI de MLFlow para confirmar que la etapa del modelo ha sido actualizada correctamente.