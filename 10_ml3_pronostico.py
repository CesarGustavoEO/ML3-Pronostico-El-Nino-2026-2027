"""ML3: Pronóstico experimental mensual Niño 3.4 (6 meses), NOAA real.
Uso: python 10_ml3_pronostico.py
Sin información futura en las variables; validación retrospectiva por año.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error

ROOT = Path(__file__).resolve().parent
CANDIDATES = [ROOT/'enso_dataset_maestro.csv', ROOT/'datos_procesados'/'enso_dataset_maestro.csv', ROOT.parent/'datos_procesados'/'enso_dataset_maestro.csv']
SOURCE = next((p for p in CANDIDATES if p.exists()), None)
if SOURCE is None:
    raise FileNotFoundError('No se encuentra enso_dataset_maestro.csv. Ponlo junto al programa o en datos_procesados/.')
OUT = ROOT/'resultados_ml3'
OUT.mkdir(exist_ok=True)
raw = pd.read_csv(SOURCE, encoding='utf-8-sig')
raw['fecha'] = pd.to_datetime(raw['fecha'])
raw = raw.sort_values('fecha').drop_duplicates('fecha').reset_index(drop=True)
required = ['anom_nino34','anom_nino3','anom_nino4','anom_nino12']
for c in required:
    raw[c] = pd.to_numeric(raw[c],errors='coerce')
if raw[required].isna().any().any():
    raise ValueError('Faltan anomalías oceánicas. Revisa el dataset NOAA.')
if not np.diff(raw['fecha'].dt.to_period('M').astype(int).to_numpy()).tolist() == [1]*(len(raw)-1):
    raise ValueError('Faltan meses consecutivos en el dataset.')
last = raw['fecha'].max()
print('NOAA:',len(raw),'meses, último:',last.strftime('%Y-%m'))

# Features observables en cada origen temporal, nunca en meses futuros.
# Los targets directos son t+1,...,t+6, cada horizonte con su propio modelo.
feature_cols=[]
for col in required:
    for lag in (0,1,2,3,5,8,11):
        name=f'{col}_lag{lag}'
        raw[name]=raw[col].shift(lag)
        feature_cols.append(name)
raw['tendencia_3m']=raw['anom_nino34']-raw['anom_nino34'].shift(3)
raw['media_3m']=raw['anom_nino34'].rolling(3).mean()
raw['media_6m']=raw['anom_nino34'].rolling(6).mean()
raw['mes_seno']=np.sin(2*np.pi*raw['fecha'].dt.month/12)
raw['mes_coseno']=np.cos(2*np.pi*raw['fecha'].dt.month/12)
feature_cols += ['tendencia_3m','media_3m','media_6m','mes_seno','mes_coseno']
for h in range(1,7):
    raw[f'target_{h}']=raw['anom_nino34'].shift(-h)

# Validación temporal: orígenes septiembre de cada año 2005-2025.
# En cada corte, entrenamiento solo con objetivos YA observados hasta ese corte.
# El primer entrenamiento comienza en 1983, con al menos 12 meses de rezago.
def train_predict(origin_idx, horizon):
    # Al predecir en origen t, target de fila s es s+h; exigir s+h <= t.
    train_end=origin_idx-horizon
    train=raw.iloc[12:train_end+1].dropna(subset=feature_cols+[f'target_{horizon}'])
    if len(train)<100:
        raise ValueError('Historial insuficiente')
    model=make_pipeline(SimpleImputer(strategy='median'),StandardScaler(),Ridge(alpha=30.0))
    model.fit(train[feature_cols],train[f'target_{horizon}'])
    return float(model.predict(raw.loc[[origin_idx],feature_cols])[0])

back=[]
for year in range(2005,2026):
    rows=raw.index[(raw['fecha'].dt.year==year)&(raw['fecha'].dt.month==9)]
    if not len(rows): continue
    i=int(rows[0])
    for h in range(1,7):
        if i+h>=len(raw): continue
        pred=train_predict(i,h)
        truth=float(raw.loc[i+h,'anom_nino34'])
        persist=float(raw.loc[i,'anom_nino34'])
        back.append({'origen':raw.loc[i,'fecha'].strftime('%Y-%m'),'fecha_objetivo':raw.loc[i+h,'fecha'].strftime('%Y-%m'),
                     'horizonte_meses':h,'observado_c':truth,'ml_c':pred,'persistencia_c':persist,
                     'error_ml_c':abs(pred-truth),'error_persistencia_c':abs(persist-truth)})
back=pd.DataFrame(back)
back.to_csv(OUT/'01_validacion_retroactiva.csv',index=False,encoding='utf-8-sig')
metrics=back.groupby('horizonte_meses').agg(n=('error_ml_c','size'),mae_ml_c=('error_ml_c','mean'),mae_persistencia_c=('error_persistencia_c','mean')).reset_index()
metrics['mejora_frente_persistencia_pct']=100*(metrics['mae_persistencia_c']-metrics['mae_ml_c'])/metrics['mae_persistencia_c']
metrics.to_csv(OUT/'02_metricas_por_horizonte.csv',index=False,encoding='utf-8-sig')

origin=len(raw)-1
# Bandas de error empíricas a partir de errores de validación retrospectiva (no intervalos calibrados).
fore=[]
for h in range(1,7):
    pred=train_predict(origin,h)
    errors=back.loc[back.horizonte_meses==h,'error_ml_c'].to_numpy()
    q=float(np.quantile(errors,.9))
    fore.append({'fecha':(last+pd.DateOffset(months=h)).strftime('%Y-%m'), 'horizonte_meses':h,
                 'pronostico_nino34_c':pred,'margen_error_historico_p90_c':q,
                 'limite_inferior_c':pred-q,'limite_superior_c':pred+q,
                 'origen_datos':last.strftime('%Y-%m'),'metodo':'Ridge directo'})
forecast=pd.DataFrame(fore)
forecast.to_csv(OUT/'03_PRONOSTICO_CONGELADO.csv',index=False,encoding='utf-8-sig')

# Analogías mayo-septiembre: sólo años anteriores con trayectoria completa posterior.
# Comparación de cuatro regiones, 5 meses, estandarización histórica.
refcols=required
hist=raw[raw.fecha.dt.year<last.year]
scales=hist[refcols].std().replace(0,1)
this=raw[(raw.fecha.dt.year==last.year)&(raw.fecha.dt.month.between(5,9))]
analog=[]
if len(this)==5 and list(this.fecha.dt.month)==[5,6,7,8,9]:
    for y in range(int(raw.fecha.dt.year.min()),last.year):
        block=raw[(raw.fecha.dt.year==y)&(raw.fecha.dt.month.between(5,9))]
        if len(block)!=5 or list(block.fecha.dt.month)!=[5,6,7,8,9]:continue
        after=raw[(raw.fecha>=pd.Timestamp(y,10,1))&(raw.fecha<=pd.Timestamp(y+1,3,1))]
        if len(after)!=6:continue
        distance=float(np.sqrt(np.mean(((block[refcols].to_numpy()-this[refcols].to_numpy())/scales.to_numpy())**2)))
        row={'anio_analogo':y,'distancia_estandarizada':distance}
        for h,v in enumerate(after['anom_nino34'],1):row[f'mes_futuro_{h}_c']=float(v)
        analog.append(row)
analog=pd.DataFrame(analog).sort_values('distancia_estandarizada')
analog.to_csv(OUT/'04_analogos_historicos.csv',index=False,encoding='utf-8-sig')

# Gráfico 1: pasado observado + futuro estimado + margen empírico
plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False})
fig,ax=plt.subplots(figsize=(12,5.8),layout='constrained')
obs=raw.tail(12)
xobs=np.arange(-len(obs)+1,1)
x=np.arange(1,7)
ax.plot(xobs,obs.anom_nino34,marker='o',lw=2.7,color='#136F8A',label='Observado NOAA')
ax.plot(np.r_[0,x],np.r_[raw.iloc[-1].anom_nino34,forecast.pronostico_nino34_c],marker='o',lw=2.8,color='#C05B37',label='Pronóstico ML')
ax.fill_between(x,forecast.limite_inferior_c,forecast.limite_superior_c,color='#C05B37',alpha=.18,label='Margen histórico de error (P90)')
ax.axvline(0,color='#666',lw=1.2,ls='--')
ax.axhline(0,color='#777',lw=.8)
labels=[d.strftime('%b %y') for d in obs.fecha]+[pd.Timestamp(s+'-01').strftime('%b %y') for s in forecast.fecha]
ax.set_xticks(np.r_[xobs,x],labels,rotation=45,ha='right')
ax.set_ylabel('Anomalía de temperatura Niño 3.4 (°C)')
ax.set_title('El Niño 2026–2027 | Lo observado y los próximos 6 meses',fontweight='bold',loc='left',pad=15)
ax.text(.01,.02,'Línea vertical: último mes observado. Banda: error retrospectivo P90, no probabilidad garantizada.',transform=ax.transAxes,fontsize=9,color='#555')
ax.legend(loc='upper left',ncol=3,frameon=False)
ax.grid(axis='y',alpha=.22)
fig.savefig(OUT/'05_PRONOSTICO_PRINCIPAL.png',dpi=180,bbox_inches='tight');plt.close(fig)

# Gráfico 2: analogías históricas vs 2026 y ML
fig,ax=plt.subplots(figsize=(11,5.6),layout='constrained')
months=['May','Jun','Jul','Ago','Sep','Oct','Nov','Dic','Ene','Feb','Mar']
for _,r in analog.head(4).iterrows():
    y=int(r.anio_analogo)
    a=raw[(raw.fecha.dt.year==y)&(raw.fecha.dt.month.between(5,9))].anom_nino34.tolist()
    b=[r[f'mes_futuro_{h}_c'] for h in range(1,7)]
    ax.plot(range(11),a+b,lw=1.8,alpha=.75,label=f'{y} (histórico)')
ax.plot(range(5),this.anom_nino34,lw=3.4,color='#151515',marker='o',label='2026 observado')
ax.plot(range(4,11),[float(this.anom_nino34.iloc[-1])]+forecast.pronostico_nino34_c.tolist(),lw=3,color='#C05B37',ls='--',marker='o',label='2026–27 ML')
ax.axvline(4,color='#777',ls='--',lw=1)
ax.set_xticks(range(11),months)
ax.set_ylabel('Anomalía Niño 3.4 (°C)')
ax.set_title('¿Qué ocurrió después de los episodios más parecidos?',loc='left',fontweight='bold',pad=12)
ax.legend(loc='upper left',ncol=3,frameon=False)
ax.grid(axis='y',alpha=.2)
fig.savefig(OUT/'06_COMPARACION_ANALOGOS.png',dpi=180,bbox_inches='tight');plt.close(fig)

# Gráfico 3: validación histórica por horizonte
fig,ax=plt.subplots(figsize=(9.5,5),layout='constrained')
w=.36; k=metrics.horizonte_meses.to_numpy()
ax.bar(k-w/2,metrics.mae_ml_c,w,label='Machine Learning',color='#136F8A')
ax.bar(k+w/2,metrics.mae_persistencia_c,w,label='Persistencia (sin ML)',color='#C05B37')
ax.set_xticks(k,[f'+{h} meses' for h in k])
ax.set_ylabel('Error absoluto medio (°C) · menor es mejor')
ax.set_title('¿El modelo supera a mantener el último valor?',fontweight='bold',loc='left')
ax.legend(frameon=False)
ax.grid(axis='y',alpha=.2)
fig.savefig(OUT/'07_VALIDACION_HISTORICA.png',dpi=180,bbox_inches='tight');plt.close(fig)

meta={'fuente':str(SOURCE),'fecha_ultimo_dato':last.strftime('%Y-%m'),'fecha_ejecucion_utc':pd.Timestamp.now(tz='UTC').isoformat(),
      'metodo':'Ridge regularizado, pronósticos directos 1-6 meses','validacion':'orígenes septiembre 2005-2025, reentrenamiento por origen y horizonte',
      'incertidumbre':'cuantil 90% del error absoluto histórico por horizonte; banda heurística no calibrada',
      'advertencia':'Pronóstico experimental Niño 3.4 mensual. No es ONI oficial, ni pronóstico oficial NOAA, ni predicción de lluvias en Perú.'}
(OUT/'08_metadatos_pronostico.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
print('\nVALIDACIÓN POR HORIZONTE:\n',metrics.round(3).to_string(index=False))
print('\nPRONÓSTICO:\n',forecast[['fecha','pronostico_nino34_c','limite_inferior_c','limite_superior_c']].round(3).to_string(index=False))
print('\nANÁLOGOS MÁS CERCANOS:\n',analog[['anio_analogo','distancia_estandarizada']].head(5).round(3).to_string(index=False))
print('\nArchivos guardados en:',OUT)
