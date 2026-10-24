"""ML3 · Explorador de pronóstico experimental Niño 3.4, datos NOAA hasta 2026-09."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title='ML 3 | El Niño 2026–2027', page_icon='🌊', layout='wide', initial_sidebar_state='expanded')
ROOT=Path(__file__).resolve().parent/'datos'
@st.cache_data
def cargar():
    hist=pd.read_csv(ROOT/'enso_dataset_maestro.csv',parse_dates=['fecha'])
    pron=pd.read_csv(ROOT/'03_PRONOSTICO_CONGELADO.csv')
    val=pd.read_csv(ROOT/'01_validacion_retroactiva.csv')
    met=pd.read_csv(ROOT/'02_metricas_por_horizonte.csv')
    ana=pd.read_csv(ROOT/'04_analogos_historicos.csv')
    info=json.loads((ROOT/'08_metadatos_pronostico.json').read_text(encoding='utf-8'))
    return hist,pron,val,met,ana,info
hist,pron,val,met,ana,info=cargar()
last=hist.sort_values('fecha').iloc[-1]
months={1:'ene',2:'feb',3:'mar',4:'abr',5:'may',6:'jun',7:'jul',8:'ago',9:'sep',10:'oct',11:'nov',12:'dic'}
def meslabel(s):
    t=pd.to_datetime(s)
    return f'{months[t.month].capitalize()} {t.year}'
def basefig(height=440):
    f=go.Figure()
    f.update_layout(height=height,template='plotly_white',margin=dict(l=12,r=12,t=35,b=12),font=dict(family='Arial',size=13,color='#172B45'),hovermode='x unified',legend=dict(orientation='h',y=1.12,x=0),paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)')
    f.update_xaxes(showgrid=False)
    f.update_yaxes(gridcolor='#E8EEF3',zeroline=True,zerolinecolor='#A3B0BD')
    return f
st.markdown('''<style>
.block-container{padding-top:1.5rem;max-width:1450px}
h1,h2,h3{color:#183047!important}
[data-testid="stMetric"]{background:#F4F8FA;border:1px solid #DEE7ED;padding:13px 17px;border-radius:12px}
</style>''',unsafe_allow_html=True)
with st.sidebar:
    st.header('🌊 Explorar ML 3')
    horizon=st.slider('¿Cuántos meses deseas ver?',1,6,6)
    histmonths=st.slider('Meses de historia visible',6,48,18,6)
    show_band=st.toggle('Mostrar margen de error histórico',True)
    st.divider()
    st.caption('**Último dato observado:** septiembre de 2026. Los meses siguientes son estimaciones experimentales.')
    st.caption('Fuente: NOAA CPC (archivo procesado); resultados generados con Ridge directo.')
    st.warning('No es un pronóstico oficial ni una alerta de lluvias para el Perú.',icon='⚠️')
st.title('🌊 ¿Cómo podría evolucionar El Niño?')
st.caption('ML 3 · Pronóstico experimental del índice mensual Niño 3.4 · Observaciones hasta septiembre de 2026')
sel=pron[pron.horizonte_meses<=horizon].copy()
end=sel.iloc[-1]
a,b,c,d=st.columns(4)
a.metric('Último dato observado',f'{last.anom_nino34:+.2f} °C',meslabel(last.fecha))
b.metric('Estimación al final del horizonte',f'{end.pronostico_nino34_c:+.2f} °C',meslabel(end.fecha))
c.metric('Cambio estimado',f'{end.pronostico_nino34_c-last.anom_nino34:+.2f} °C','Frente a sep. 2026',delta_color='off')
d.metric('Error medio histórico del ML',f'{met.loc[met.horizonte_meses==horizon,"mae_ml_c"].iloc[0]:.2f} °C',f'A {horizon} mes(es)')
t1,t2,t3,t4=st.tabs(['📈 Pronóstico','🕰️ Comparación histórica','🧪 ¿Acertó el modelo?','📚 Datos y método'])
with t1:
    st.subheader('Lo observado y lo estimado, sin confundirlos')
    h=hist.sort_values('fecha').tail(histmonths)
    f=basefig(510)
    if show_band:
        f.add_trace(go.Scatter(x=sel.fecha,y=sel.limite_superior_c,mode='lines',line=dict(width=0),hoverinfo='skip',showlegend=False))
        f.add_trace(go.Scatter(x=sel.fecha,y=sel.limite_inferior_c,mode='lines',line=dict(width=0),fill='tonexty',fillcolor='rgba(231,147,60,.20)',name='Margen de error histórico (orientativo)',hovertemplate='%{y:.2f} °C<extra></extra>'))
    f.add_trace(go.Scatter(x=h.fecha,y=h.anom_nino34,mode='lines+markers',line=dict(color='#087E8B',width=4),marker=dict(size=6),name='Observado · NOAA',hovertemplate='%{y:+.2f} °C<extra></extra>'))
    f.add_trace(go.Scatter(x=[h.fecha.iloc[-1]]+sel.fecha.tolist(),y=[float(h.anom_nino34.iloc[-1])]+sel.pronostico_nino34_c.tolist(),mode='lines+markers',line=dict(color='#E58C36',width=4,dash='dash'),marker=dict(size=8),name='Pronóstico · ML',hovertemplate='%{y:+.2f} °C<extra></extra>'))
    f.add_vline(x=h.fecha.iloc[-1].timestamp()*1000,line_color='#63788D',line_dash='dot')
    f.update_yaxes(title='Anomalía Niño 3.4 (°C)')
    st.plotly_chart(f,use_container_width=True)
    st.info(f'**Lectura sencilla:** el modelo estima que la anomalía pase de {last.anom_nino34:+.2f} °C a {end.pronostico_nino34_c:+.2f} °C hacia {meslabel(end.fecha)}. Es una estimación, no una certeza.')
    st.caption('La franja sombreada se calcula con el percentil 90 de errores absolutos históricos por horizonte. No es un intervalo de confianza ni una probabilidad calibrada del 90 %.')
    with st.expander('Ver los valores mensuales y descargarlos'):
        view=sel[['fecha','pronostico_nino34_c','limite_inferior_c','limite_superior_c']].rename(columns={'fecha':'Mes','pronostico_nino34_c':'Estimación °C','limite_inferior_c':'Límite orientativo inferior °C','limite_superior_c':'Límite orientativo superior °C'})
        st.dataframe(view,use_container_width=True,hide_index=True)
        st.download_button('Descargar pronóstico congelado',pron.to_csv(index=False).encode('utf-8-sig'),'ML3_pronostico_congelado.csv','text/csv')
with t2:
    st.subheader('¿Qué ocurrió después en años parecidos?')
    st.caption('La semejanza se calculó con datos históricos previos a octubre; las trayectorias siguientes son observaciones de aquellos años, no pronósticos actuales.')
    top=ana.sort_values('distancia_estandarizada').head(10)
    years=st.multiselect('Años para comparar',top.anio_analogo.astype(int).tolist(),default=top.anio_analogo.astype(int).head(3).tolist(),max_selections=5)
    f=basefig(470)
    f.add_trace(go.Scatter(x=list(range(1,horizon+1)),y=sel.pronostico_nino34_c,mode='lines+markers',name='Pronóstico 2026–27',line=dict(color='#E58C36',width=5),marker=dict(size=9)))
    palette=['#2463A5','#13856C','#9A4C86','#687E35','#98643B']
    for i,yr in enumerate(years):
        row=ana[ana.anio_analogo==yr].iloc[0]
        f.add_trace(go.Scatter(x=list(range(1,horizon+1)),y=[row[f'mes_futuro_{j}_c'] for j in range(1,horizon+1)],mode='lines+markers',name=str(yr),line=dict(color=palette[i],width=2.5)))
    f.update_xaxes(title='Meses posteriores a septiembre',tickmode='array',tickvals=list(range(1,horizon+1)),ticktext=[meslabel(x) for x in sel.fecha])
    f.update_yaxes(title='Anomalía Niño 3.4 (°C)')
    st.plotly_chart(f,use_container_width=True)
    st.caption('Distancia menor = mayor similitud bajo el método utilizado; no significa que el futuro de 2026 tenga que repetirse.')
    st.dataframe(top[['anio_analogo','distancia_estandarizada']].rename(columns={'anio_analogo':'Año histórico','distancia_estandarizada':'Distancia de similitud'}),hide_index=True,use_container_width=True)
with t3:
    st.subheader('¿El ML predice mejor que repetir el último valor?')
    st.caption('Prueba retrospectiva: cada septiembre de 2005 a 2025 se pronosticaron los seis meses siguientes, sin utilizar sus observaciones al entrenar.')
    f=basefig(430)
    f.add_trace(go.Bar(x=met.horizonte_meses,y=met.mae_ml_c,name='ML Ridge',marker_color='#E58C36',text=[f'{x:.2f}' for x in met.mae_ml_c],textposition='outside'))
    f.add_trace(go.Bar(x=met.horizonte_meses,y=met.mae_persistencia_c,name='Persistencia',marker_color='#087E8B',text=[f'{x:.2f}' for x in met.mae_persistencia_c],textposition='outside'))
    f.update_layout(barmode='group',yaxis_title='Error absoluto medio (°C) · menor es mejor',xaxis_title='Horizonte (meses)')
    st.plotly_chart(f,use_container_width=True)
    better=int((met.mae_ml_c<met.mae_persistencia_c).sum())
    st.warning(f'**Resultado de la validación:** el ML supera a la persistencia en {better} de 6 horizontes. Por tanto, no está demostrada una ventaja consistente del modelo.',icon='🔎')
    st.divider()
    st.subheader('Revisa una prueba histórica concreta')
    yr=st.select_slider('Año de origen (septiembre)',options=sorted(pd.to_datetime(val.origen).dt.year.unique().tolist()),value=2023)
    v=val[pd.to_datetime(val.origen).dt.year==yr].sort_values('horizonte_meses')
    f=basefig(390)
    for col,name,color in [('observado_c','Lo que ocurrió','#087E8B'),('ml_c','Lo que predijo ML','#E58C36'),('persistencia_c','Persistencia','#8C9BA9')]:
        f.add_trace(go.Scatter(x=v.fecha_objetivo,y=v[col],mode='lines+markers',name=name,line=dict(color=color,width=3)))
    f.update_yaxes(title='Anomalía Niño 3.4 (°C)')
    f.update_xaxes(title='Mes evaluado')
    st.plotly_chart(f,use_container_width=True)
    st.caption('Estas pruebas históricas son distintas del pronóstico congelado de octubre de 2026 a marzo de 2027.')
    st.download_button('Descargar validación histórica',val.to_csv(index=False).encode('utf-8-sig'),'ML3_validacion.csv','text/csv')
with t4:
    st.subheader('Transparencia metodológica')
    st.markdown('''**Pregunta:** ¿Cómo podría evolucionar la anomalía mensual de temperatura superficial del mar en la región Niño 3.4 durante los seis meses posteriores a septiembre de 2026?

**Datos:** serie mensual NOAA CPC procesada, enero de 1982 a septiembre de 2026. La variable objetivo es la anomalía mensual Niño 3.4, no el índice ONI oficial de tres meses.

**Algoritmo:** regresión Ridge regularizada, seis pronósticos directos (uno por horizonte).

**Comparación:** persistencia del último valor observado y búsqueda de episodios históricos similares.

**Evaluación:** orígenes de septiembre de 2005 a 2025, con reentrenamiento retrospectivo; 21 casos por horizonte. MAE en °C.

**Límites:** el modelo no supera consistentemente la persistencia; la banda de incertidumbre es orientativa y no está calibrada como intervalo probabilístico. No predice lluvia, inundaciones ni impactos por departamento.

**Reproducibilidad:** conservar el CSV de pronóstico congelado y los metadatos antes de actualizar los datos NOAA, para contrastar posteriormente los pronósticos con observaciones.''')
    st.json({k:v for k,v in info.items() if k!='fuente'},expanded=False)
    st.download_button('Descargar métricas por horizonte',met.to_csv(index=False).encode('utf-8-sig'),'ML3_metricas.csv','text/csv')
st.divider()
st.caption('Investigación académica · ML 3 · NOAA CPC · Fecha de corte: septiembre de 2026 · Resultados experimentales, no oficiales.')
