"""ML3 — Informe interactivo de anomalías Niño 3.4, datos NOAA a septiembre 2026."""
from pathlib import Path
import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="ML 03 | Perspectiva del Pacífico", page_icon="📈", layout="wide", initial_sidebar_state="collapsed")
DATA = Path(__file__).resolve().parent / "datos"
INK="#172C39"; MUTED="#60717B"; TEAL="#087B83"; COPPER="#BD7141"; GRID="#E7ECEE"; PALE="#F5F7F7"

@st.cache_data
def load():
    hist=pd.read_csv(DATA/"enso_dataset_maestro.csv",parse_dates=["fecha"]).sort_values("fecha")
    pron=pd.read_csv(DATA/"03_PRONOSTICO_CONGELADO.csv");pron["fecha"]=pd.to_datetime(pron["fecha"])
    val=pd.read_csv(DATA/"01_validacion_retroactiva.csv")
    met=pd.read_csv(DATA/"02_metricas_por_horizonte.csv")
    ana=pd.read_csv(DATA/"04_analogos_historicos.csv").sort_values("distancia_estandarizada")
    info=json.loads((DATA/"08_metadatos_pronostico.json").read_text(encoding="utf-8"))
    return hist,pron,val,met,ana,info
hist,pron,val,met,ana,info=load()
last=hist.iloc[-1]

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Libre+Baskerville:wght@400;700&display=swap');
html,body,[class*="css"],.stApp {font-family:'DM Sans',sans-serif;color:#172C39}
.stApp{background:#FFFFFF}
.block-container{max-width:1180px;padding-top:2.4rem;padding-bottom:3rem}
h1,h2,h3{font-family:'DM Sans',sans-serif!important;letter-spacing:-.035em!important;color:#172C39!important}
h1{font-size:2.6rem!important;font-weight:700!important}
h2{font-size:1.55rem!important;font-weight:650!important}
h3{font-size:1.12rem!important}
[data-testid="stMetric"]{background:#F5F7F7;padding:18px 20px;border-top:2px solid #DCE4E5;border-radius:2px}
[data-testid="stMetricLabel"]{font-size:.84rem!important;color:#60717B!important}
[data-testid="stMetricValue"]{font-size:1.85rem!important;color:#172C39!important}
[data-testid="stTabs"] button{font-weight:600}
[data-testid="stTabs"] button[aria-selected="true"]{color:#087B83!important}
.stMarkdown p{line-height:1.6}
.eyebrow{font-size:.73rem;letter-spacing:.17em;text-transform:uppercase;color:#60717B;font-weight:700;margin-bottom:12px}
.deck{font-size:1.07rem;color:#536774;max-width:800px;line-height:1.7;margin:0 0 20px}
.rule{border-top:1px solid #DCE4E5;margin:24px 0}
.note{border-left:3px solid #BD7141;background:#F8F6F2;padding:14px 18px;font-size:.92rem;line-height:1.65}
.section-number{color:#BD7141;font-size:.78rem;font-weight:700;letter-spacing:.12em}
.small-note{color:#60717B;font-size:.83rem;line-height:1.6}
</style>""",unsafe_allow_html=True)

def fig(height=420):
    f=go.Figure()
    f.update_layout(height=height,template="plotly_white",font=dict(family="Arial",color=INK,size=12),margin=dict(l=10,r=22,t=35,b=15),paper_bgcolor="white",plot_bgcolor="white",hovermode="x unified",legend=dict(orientation="h",x=0,y=1.15,font=dict(size=12)),hoverlabel=dict(bgcolor="white",font_color=INK),showlegend=True)
    f.update_xaxes(showgrid=False,showline=True,linecolor="#B6C2C6",tickfont=dict(color=MUTED))
    f.update_yaxes(gridcolor=GRID,zeroline=True,zerolinecolor="#B9C5C9",tickfont=dict(color=MUTED))
    return f

def month(d):
    return pd.to_datetime(d).strftime("%m/%Y")

st.markdown('<div class="eyebrow">UNIVERSIDAD NACIONAL DEL ALTIPLANO  /  VISUALIZACIÓN DE DATOS  /  MÓDULO 03</div>',unsafe_allow_html=True)
st.title("Perspectiva del Pacífico 2026–2027")
st.markdown('<div class="deck">Evolución observada de la anomalía Niño 3.4 y proyección experimental a seis meses. Una lectura visual que distingue evidencia histórica, estimación e incertidumbre.</div>',unsafe_allow_html=True)
st.markdown('<div class="rule"></div>',unsafe_allow_html=True)

with st.container():
    c1,c2,c3=st.columns([1,1,2],gap="large")
    with c1: horizon=st.selectbox("Horizonte de análisis",options=[1,2,3,4,5,6],index=5,format_func=lambda x:f"{x} {'mes' if x==1 else 'meses'}")
    with c2: history=st.selectbox("Historia visible",options=[12,18,24,36],index=1,format_func=lambda x:f"{x} meses")
    with c3: show_band=st.toggle("Mostrar amplitud del error histórico",value=True,help="La banda usa el percentil 90 del error absoluto histórico por horizonte. No es un intervalo probabilístico calibrado.")
sel=pron[pron.horizonte_meses<=horizon].copy(); end=sel.iloc[-1]
metrics=met.loc[met.horizonte_meses==horizon].iloc[0]
a,b,c,d=st.columns(4,gap="medium")
a.metric("Último registro · sep. 2026",f"{last.anom_nino34:+.2f} °C")
b.metric(f"Estimación · {month(end.fecha)}",f"{end.pronostico_nino34_c:+.2f} °C")
c.metric("Variación proyectada",f"{end.pronostico_nino34_c-last.anom_nino34:+.2f} °C")
d.metric(f"MAE retrospectivo · {horizon} m",f"{metrics.mae_ml_c:.2f} °C")
st.markdown('<div class="rule"></div>',unsafe_allow_html=True)

t1,t2,t3,t4=st.tabs(["01  Evolución y pronóstico","02  Episodios comparables","03  Validación","04  Datos y método"])
with t1:
    st.markdown('<div class="section-number">FIGURA 01 / SERIE TEMPORAL</div>',unsafe_allow_html=True)
    st.subheader("De la observación a la estimación")
    st.caption("Anomalía de temperatura superficial del mar en Niño 3.4 (°C respecto a la referencia climatológica NOAA).")
    h=hist.tail(history)
    f=fig(475)
    if show_band:
        xx=[h.fecha.iloc[-1]]+sel.fecha.tolist()
        lower=[float(h.anom_nino34.iloc[-1])]+sel.limite_inferior_c.tolist()
        upper=[float(h.anom_nino34.iloc[-1])]+sel.limite_superior_c.tolist()
        f.add_trace(go.Scatter(x=xx,y=upper,mode="lines",line=dict(width=0),showlegend=False,hoverinfo="skip"))
        f.add_trace(go.Scatter(x=xx,y=lower,mode="lines",line=dict(width=0),fill="tonexty",fillcolor="rgba(189,113,65,.12)",name="Error histórico · referencia",showlegend=False,hoverinfo="skip"))
    f.add_trace(go.Scatter(x=h.fecha,y=h.anom_nino34,mode="lines+markers",name="Observado · NOAA",line=dict(color=TEAL,width=3),marker=dict(size=5),hovertemplate="%{x|%b %Y}<br>%{y:+.2f} °C<extra>Observado</extra>"))
    f.add_trace(go.Scatter(x=[h.fecha.iloc[-1]]+sel.fecha.tolist(),y=[float(h.anom_nino34.iloc[-1])]+sel.pronostico_nino34_c.tolist(),mode="lines+markers",name="Proyección · Ridge",line=dict(color=COPPER,width=3,dash="dash"),marker=dict(size=7),hovertemplate="%{x|%b %Y}<br>%{y:+.2f} °C<extra>Estimación</extra>"))
    f.add_vline(x=h.fecha.iloc[-1].timestamp()*1000,line=dict(color="#99A9B0",width=1,dash="dot"))
    # Etiquetas directas fuera del trazado, igual que en la Figura 02.
    # La observación termina en septiembre; la proyección termina en el mes seleccionado.
    from datetime import timedelta
    obs_date=pd.Timestamp(h.fecha.iloc[-1])
    pred_date=pd.Timestamp(sel.fecha.iloc[-1])
    obs_value=float(h.anom_nino34.iloc[-1])
    pred_value=float(sel.pronostico_nino34_c.iloc[-1])
    label_date=pred_date+timedelta(days=14)
    right_edge=pred_date+timedelta(days=83)
    # La etiqueta del tramo observado se ubica junto al corte histórico,
    # evitando confundirla con la curva de pronóstico.
    f.add_annotation(x=obs_date,y=obs_value,xref="x",yref="y",
                     text="<b>Observado · NOAA</b>",showarrow=True,ax=-90,ay=-32,
                     arrowhead=0,arrowwidth=1,arrowcolor=TEAL,
                     font=dict(family="Arial",size=11,color=TEAL),
                     bgcolor="rgba(255,255,255,0.96)")
    f.add_shape(type="line",xref="x",yref="y",x0=pred_date,x1=label_date,
                y0=pred_value,y1=pred_value,line=dict(color=COPPER,width=1))
    f.add_annotation(x=label_date,y=pred_value,xref="x",yref="y",
                     text=f"<b>Pronóstico · {pred_value:+.2f} °C</b>",
                     showarrow=False,xanchor="left",yanchor="middle",xshift=5,
                     font=dict(family="Arial",size=11,color=COPPER),
                     bgcolor="rgba(255,255,255,0.96)")
    f.update_layout(showlegend=False,margin=dict(l=10,r=18,t=32,b=15))
    f.update_xaxes(range=[pd.Timestamp(h.fecha.iloc[0])-timedelta(days=12),right_edge])
    f.update_yaxes(title="Anomalía (°C)")
    st.plotly_chart(f,use_container_width=True,config={"displaylogo":False})
    st.markdown(f'<div class="note"><strong>Hallazgo principal.</strong> Desde {last.anom_nino34:+.2f} °C en septiembre de 2026, el modelo estima {end.pronostico_nino34_c:+.2f} °C en {month(end.fecha)}. La trayectoria proyectada no constituye una observación ni una previsión oficial.</div>',unsafe_allow_html=True)
    st.markdown('<p class="small-note">La banda representa el percentil 90 de errores absolutos retrospectivos por horizonte; no equivale a un intervalo de confianza del 90 %.</p>',unsafe_allow_html=True)
    with st.expander("Tabla de resultados y descarga"):
        st.dataframe(sel[["fecha","pronostico_nino34_c","limite_inferior_c","limite_superior_c"]],hide_index=True,use_container_width=True)
        st.download_button("Descargar proyecciones (CSV)",pron.to_csv(index=False).encode("utf-8-sig"),"ML3_pronostico.csv","text/csv")
with t2:
    st.markdown('<div class="section-number">FIGURA 02 / CONTEXTO HISTÓRICO</div>',unsafe_allow_html=True)
    st.subheader("Qué ocurrió después en episodios comparables")
    st.caption("Las curvas históricas muestran hechos observados en otros años; no representan escenarios probabilísticos para 2026.")
    years=st.multiselect("Seleccionar episodios",ana.anio_analogo.astype(int).head(10).tolist(),default=ana.anio_analogo.astype(int).head(3).tolist(),max_selections=4)
    f=fig(465)
    colors=["#536C83","#7C8D83","#9A8E7B","#9B8190"]
    endpoints=[]
    for i,year in enumerate(years):
        row=ana[ana.anio_analogo==year].iloc[0]
        vals=[float(row[f"mes_futuro_{j}_c"]) for j in range(1,horizon+1)]
        f.add_trace(go.Scatter(x=sel.fecha,y=vals,mode="lines+markers",name=f"Episodio {year}",showlegend=False,line=dict(color=colors[i],width=2),marker=dict(size=5)))
        endpoints.append((f"{year}",vals[-1],colors[i]))
    forecast_vals=sel.pronostico_nino34_c.astype(float).tolist()
    f.add_trace(go.Scatter(x=sel.fecha,y=forecast_vals,mode="lines+markers",name="Proyección 2026–27",showlegend=False,line=dict(color=COPPER,width=4,dash="dash"),marker=dict(size=7)))
    endpoints.append(("Pronóstico 2026–27",forecast_vals[-1],COPPER))

    # Etiquetas directas, al final de las líneas y FUERA del área de datos.
    # Se separan verticalmente para que no se superpongan cuando las curvas convergen.
    from datetime import timedelta
    final_date=pd.Timestamp(sel.fecha.iloc[-1])
    label_date=final_date+timedelta(days=13)
    max_date=final_date+timedelta(days=73)
    all_values=[]
    for trace in f.data:
        all_values.extend(float(v) for v in trace.y if pd.notna(v))
    ymin=min(all_values); ymax=max(all_values)
    yrange=max(ymax-ymin,0.8)
    padding=yrange*0.13
    y_low=ymin-padding; y_high=ymax+padding
    min_gap=(y_high-y_low)*0.077
    ordered=sorted(enumerate(endpoints),key=lambda pair:pair[1][1])
    positions={}
    for rank,(original,(label,value,color)) in enumerate(ordered):
        positions[original]=max(value, (positions[ordered[rank-1][0]]+min_gap) if rank else value)
    overflow=max(positions.values())-(y_high-min_gap*0.2) if positions else 0
    if overflow>0:
        positions={k:v-overflow for k,v in positions.items()}
    for i,(label,value,color) in enumerate(endpoints):
        adjusted=positions[i]
        # Una guía fina une el valor real con su etiqueta desplazada.
        f.add_shape(type="line",xref="x",yref="y",x0=final_date,x1=label_date,y0=value,y1=adjusted,line=dict(color=color,width=1))
        f.add_annotation(x=label_date,y=adjusted,xref="x",yref="y",text=f"<b>{label}</b>",showarrow=False,xanchor="left",yanchor="middle",xshift=5,font=dict(family="Arial",size=11,color=color),bgcolor="rgba(255,255,255,0.93)")
    f.update_layout(margin=dict(l=10,r=15,t=22,b=15),showlegend=False)
    f.update_xaxes(range=[pd.Timestamp(sel.fecha.iloc[0])-timedelta(days=12),max_date],title=None)
    f.update_yaxes(title="Anomalía Niño 3.4 (°C)",range=[y_low,y_high])
    st.plotly_chart(f,use_container_width=True,config={"displaylogo":False})
    st.markdown('<p class="small-note">Una distancia estandarizada menor indica mayor parecido bajo el método de búsqueda empleado. No garantiza que las trayectorias futuras se repitan.</p>',unsafe_allow_html=True)
    with st.expander("Consultar distancias históricas"):
        st.dataframe(ana[["anio_analogo","distancia_estandarizada"]].rename(columns={"anio_analogo":"Año","distancia_estandarizada":"Distancia estandarizada"}),hide_index=True,use_container_width=True)
with t3:
    st.markdown('<div class="section-number">FIGURA 03 / EVALUACIÓN DEL MODELO</div>',unsafe_allow_html=True)
    st.subheader("¿Mejora el modelo a una referencia sencilla?")
    st.caption("Error absoluto medio (MAE) en 21 pruebas históricas por horizonte. Cuanto menor, mejor.")
    f=fig(410)
    f.add_trace(go.Bar(x=met.horizonte_meses,y=met.mae_ml_c,name="Ridge · ML",marker_color=COPPER,text=[f"{x:.2f}" for x in met.mae_ml_c],textposition="outside"))
    f.add_trace(go.Bar(x=met.horizonte_meses,y=met.mae_persistencia_c,name="Persistencia",marker_color=TEAL,text=[f"{x:.2f}" for x in met.mae_persistencia_c],textposition="outside"))
    f.update_layout(barmode="group",bargap=.24)
    f.update_xaxes(title="Meses desde el origen",tickmode="linear",dtick=1)
    f.update_yaxes(title="MAE (°C)",rangemode="tozero")
    st.plotly_chart(f,use_container_width=True,config={"displaylogo":False})
    better=int((met.mae_ml_c<met.mae_persistencia_c).sum())
    st.markdown(f'<div class="note"><strong>Lectura de validación.</strong> Ridge obtiene menor MAE que persistencia en {better} de 6 horizontes. Los resultados no acreditan una superioridad consistente del modelo.</div>',unsafe_allow_html=True)
    st.markdown("#### Una prueba retrospectiva, paso a paso")
    years=sorted(pd.to_datetime(val.origen).dt.year.unique().tolist())
    yr=st.select_slider("Septiembre utilizado como origen",options=years,value=2023 if 2023 in years else years[-1])
    v=val[pd.to_datetime(val.origen).dt.year==yr].sort_values("horizonte_meses")
    f=fig(370)
    for col,name,color,dash in [("observado_c","Observado",TEAL,"solid"),("ml_c","Ridge · ML",COPPER,"dash"),("persistencia_c","Persistencia","#82939C","dot")]:
        f.add_trace(go.Scatter(x=v.fecha_objetivo,y=v[col],mode="lines+markers",name=name,line=dict(color=color,width=3,dash=dash)))
    f.update_yaxes(title="Anomalía (°C)")
    st.plotly_chart(f,use_container_width=True,config={"displaylogo":False})
    st.download_button("Descargar validación (CSV)",val.to_csv(index=False).encode("utf-8-sig"),"ML3_validacion.csv","text/csv")
with t4:
    st.markdown('<div class="section-number">ANEXO / TRANSPARENCIA</div>',unsafe_allow_html=True)
    st.subheader("Datos, método y alcance")
    st.markdown("""**Pregunta de investigación.** ¿Cómo podría evolucionar la anomalía mensual Niño 3.4 durante los seis meses posteriores a septiembre de 2026?

**Fuente.** NOAA CPC; serie mensual procesada de enero de 1982 a septiembre de 2026. La anomalía Niño 3.4 no debe confundirse con la temperatura absoluta del mar ni con el índice ONI oficial.

**Modelo.** Regresión Ridge, seis horizontes directos. Comparación con persistencia y episodios históricos.

**Validación.** Orígenes de septiembre de 2005 a 2025 (21 por horizonte), con reentrenamiento retrospectivo; MAE en grados Celsius.

**Limitaciones.** Modelo experimental sin superioridad consistente frente a persistencia. No pronostica precipitaciones ni impactos regionales. La banda de error es orientativa, no un intervalo probabilístico calibrado.

**Trazabilidad.** Los archivos de resultados y metadatos se conservan congelados para su posterior contraste con observaciones.""")
    with st.expander("Metadatos técnicos"):
        st.json(info,expanded=False)
    st.download_button("Descargar métricas (CSV)",met.to_csv(index=False).encode("utf-8-sig"),"ML3_metricas.csv","text/csv")
st.markdown('<div class="rule"></div>',unsafe_allow_html=True)
st.markdown('<div class="small-note">UNAP · Maestría en Ciencia de Datos · Visualización de Datos &nbsp;&nbsp; | &nbsp;&nbsp; NOAA CPC · Corte de observación: septiembre de 2026 &nbsp;&nbsp; | &nbsp;&nbsp; Investigación académica, no oficial.</div>',unsafe_allow_html=True)
