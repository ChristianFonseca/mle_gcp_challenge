# Monitoreo y Evaluación de Modelos ML

## 1. ¿Por Qué Monitorear?

Una vez que nuestro modelo de predicción de churn está en producción y sirviendo predicciones a través de un endpoint, nuestro trabajo apenas comienza. El monitoreo continuo es esencial para mantener la efectividad del modelo a lo largo del tiempo, ya que múltiples factores pueden afectar su rendimiento:

- **Data Drift**: Las características estadísticas de los datos de entrada cambian. Por ejemplo, si lanzamos una campaña en una nueva región, la edad promedio (`age`) o el valor de compra (`avg_purchase_value`) de los nuevos clientes podría ser muy diferente a los datos con los que se entrenó el modelo.

- **Concept Drift**: La relación entre las características y el resultado (el churn) cambia. Por ejemplo, una nueva funcionalidad en la app podría hacer que el indicador `is_active` ya no sea tan relevante para predecir el abandono como antes.

Un sistema de monitoreo robusto nos permite detectar estas derivas y caídas de rendimiento de forma proactiva, asegurando la fiabilidad y el ROI del modelo a largo plazo.

## 2. Selección y Cálculo de Métricas

Para un monitoreo completo, rastreamos tres categorías de métricas:

### a. Métricas de Rendimiento del Modelo (Online)

Estas métricas miden la calidad predictiva del modelo con datos reales. Requieren "ground truth" (saber si el cliente realmente abandonó), lo cual puede tener una demora (ej. un mes).

- **ROC AUC**: Sigue siendo una métrica excelente para evaluar el poder de discriminación general del modelo. Un descenso sostenido es una clara señal de degradación.

- **Precision vs. Recall**: En un problema de churn, este balance es crítico.
  - **Alta Precisión**: Si el modelo dice que un cliente abandonará, es muy probable que lo haga. Esto es para no malgastar recursos en clientes que no pensaban irse.
  - **Alto Recall**: El modelo es bueno capturando a la mayoría de los clientes que realmente van a abandonar. Esto es para no perder oportunidades de retención.

- **Log-Loss**: Mide qué tan "calibradas" están las probabilidades que entrega el modelo. Un aumento en el log-loss indica que la confianza del modelo en sus predicciones está disminuyendo.

### b. Métricas de Deriva (Drift)

Estas son nuestras señales de alerta temprana, ya que no requieren ground truth. Podemos calcularlas casi en tiempo real.

- **Deriva de Características (Feature Drift)**: Comparamos la distribución estadística de las características de entrada del tráfico en vivo con la distribución de los datos de entrenamiento.

- **Deriva de Predicciones (Prediction Drift)**: Comparamos la distribución de las predicciones del modelo (las probabilidades de churn) entre el entorno de producción y el de entrenamiento. Un cambio brusco puede indicar que el modelo está viendo datos muy diferentes.

### c. Métricas Operacionales

Estas miden la salud de la infraestructura que sirve el modelo:

- **Latencia**: Tiempo que tarda el modelo en devolver una predicción. Debe ser bajo para no afectar la experiencia de usuario.

- **Tasa de Errores**: Porcentaje de solicitudes que fallan (ej. errores 5xx).

- **Tráfico (QPS)**: Cantidad de predicciones por segundo que procesa el sistema.

## 3. Propuesta de Sistema de Monitoreo y Alertas

Proponemos una arquitectura en GCP que automatice este proceso, utilizando Vertex AI Model Monitoring como pieza central:

1. **Activación**: Al desplegar el modelo en un Vertex AI Endpoint, se activa Vertex AI Model Monitoring.

2. **Línea Base (Baseline)**: Se le proporciona al sistema de monitoreo una referencia de los datos de entrenamiento. Vertex AI calculará las estadísticas de estas características.

3. **Captura de Datos**: El endpoint automáticamente captura una muestra de las solicitudes de predicción en vivo.

4. **Detección de Deriva**: Periódicamente (ej. cada hora), Vertex AI compara la distribución de los datos en vivo con la línea base y calcula la distancia estadística (ej. L-infinito, DJS) para cada característica.

5. **Alertas**:
   - Se configura un umbral de alerta para cada característica (ej. alertar si la distancia estadística supera 0.3).
   - Si se supera el umbral, Vertex AI Model Monitoring puede enviar una alerta a Cloud Logging.
   - Desde Cloud Logging, se configura una alerta que notifique al equipo de MLOps a través de Email, Slack o PagerDuty.

6. **Dashboard**: Vertex AI proporciona un dashboard nativo para visualizar la deriva de cada característica a lo largo del tiempo, permitiendo un análisis rápido de qué está cambiando.

7. **Monitoreo de Rendimiento**: Para las métricas que requieren ground truth, se puede programar un Notebook de Vertex AI o una Cloud Function que se ejecute semanalmente, una los logs de predicción con los datos reales de churn de BigQuery, calcule el ROC AUC y otras métricas, y las envíe a Cloud Monitoring como una métrica personalizada. Desde ahí, se pueden crear dashboards y alertas si el rendimiento cae.

## 4. Estrategias de Validación y Recuperación: Test A/B y Rollback

Cuando tenemos un nuevo modelo candidato (el "challenger") que superó al actual ("champion") en la evaluación offline, no lo desplegamos directamente.

### Test A/B (Champion vs. Challenger)

La mejor práctica es realizar una prueba online para ver cómo se comporta el nuevo modelo con datos reales.

- **Implementación**: Los Vertex AI Endpoints soportan de forma nativa la división de tráfico.
  - Desplegamos el modelo "challenger" en el mismo endpoint que el "champion".
  - Configuramos la división de tráfico:
    - 90% del tráfico se sigue enviando al modelo champion (actual en producción).
    - 10% del tráfico se desvía al modelo challenger.
  - Monitoreamos el rendimiento (y el impacto en el negocio) de ambas versiones del modelo en paralelo durante un periodo de tiempo definido (ej. dos semanas).
  - Si el challenger demuestra ser superior de forma consistente, gradualmente aumentamos su tráfico hasta el 100%, convirtiéndolo en el nuevo champion.

### Rollback

Es la estrategia de seguridad para recuperarse rápidamente de un despliegue fallido.

- **¿Cuándo hacer un rollback?**
  - **Fallo catastrófico inmediato**: La latencia se dispara o la tasa de errores supera el umbral crítico.
  - **Rendimiento degradado severo**: Un monitoreo cercano post-despliegue revela que las predicciones del nuevo modelo son muy pobres o sesgadas.

- **Implementación**:
  - **Manual**: Si se está usando la división de tráfico, el rollback es tan simple como reconfigurar el endpoint para que el 100% del tráfico vuelva al modelo champion anterior. Esto se puede hacer en segundos desde la consola de GCP o con un comando gcloud.
  - **Automatizado**: Para sistemas críticos, una alerta de Cloud Monitoring (ej. "Tasa de errore > 5%") puede disparar una Cloud Function que ejecute automáticamente el comando de gcloud para revertir el tráfico, minimizando el tiempo de impacto. El Vertex AI Model Registry, ya que mantiene un historial versionado de los modelos que se pueden redesplegar.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.
