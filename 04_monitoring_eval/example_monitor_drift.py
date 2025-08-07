import pandas as pd
import numpy as np
from scipy.stats import ks_2samp

# Cargar la distribución de 'entrenamiento' (nuestra línea base)
# En un escenario real, esto sería un perfil estadístico guardado de los datos de entrenamiento.
baseline_data = pd.read_csv('../00_data/clientes.csv')
baseline_feature = baseline_data['avg_purchase_value'].dropna()

# Simular datos 'en vivo' donde la distribución ha cambiado
# Por ejemplo, una campaña atrajo a clientes de mayor poder adquisitivo.
live_data_simulation = {
    'avg_purchase_value': np.random.normal(loc=350, scale=80, size=1000) # El promedio original era ~255
}
live_df = pd.DataFrame(live_data_simulation)
live_feature = live_df['avg_purchase_value']

# Aplicar el test de Kolmogorov-Smirnov
ks_statistic, p_value = ks_2samp(baseline_feature, live_feature)

print(f"Resultado del Test K-S para 'avg_purchase_value':")
print(f"Estadístico K-S: {ks_statistic:.4f}")
print(f"P-valor: {p_value:.4f}")

# 4. Tomar una decisión basada en el p-valor
alpha = 0.05  # Umbral de significancia
if p_value < alpha:
    print(f"\nAlerta: Se ha detectado un data drift significativo (p < {alpha}). "
          f"La distribución de la característica ha cambiado.")
else:
    print(f"\nOK: No se ha detectado un data drift significativo (p >= {alpha}).")