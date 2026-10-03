#!/usr/bin/env python3
import csv, re
from datetime import datetime
from pathlib import Path

BASE=Path(__file__).resolve().parent
ORIGEM=BASE/"origem"
OUT=BASE/"trusted"
OUT.mkdir(parents=True,exist_ok=True)

COLS=["agendamento_id","paciente_id","unidade_id","estado_unidade","regiao_unidade","sexo",
"faixa_etaria","especialidade","profissional_id","data_agendamento","data_consulta","hora_consulta",
"status","canal_agendamento","tipo_consulta","valor_consulta","dias_antecedencia",
"no_shows_anteriores","sistema_origem"]

SEX={"M":"MASCULINO","MASC":"MASCULINO","MASCULINO":"MASCULINO","MALE":"MASCULINO",
     "F":"FEMININO","FEM":"FEMININO","FEMININO":"FEMININO","FEMALE":"FEMININO"}
STA={"NO_SHOW":"NO_SHOW","NO-SHOW":"NO_SHOW","FALTOU":"NO_SHOW","AUSENTE":"NO_SHOW",
     "REALIZADO":"REALIZADO","DONE":"REALIZADO","ATENDIDO":"REALIZADO",
     "CANCELADO":"CANCELADO","CANCELLED":"CANCELADO","AGENDADO":"AGENDADO",
     "SCHEDULED":"AGENDADO","CONFIRMADO":"CONFIRMADO","CONFIRMED":"CONFIRMADO"}
ESP={"CARDIOLOGIA":"Cardiologia","CARDIO":"Cardiologia","CARD":"Cardiologia",
     "DERMATOLOGIA":"Dermatologia","DERMA":"Dermatologia","ORTOPEDIA":"Ortopedia",
     "ORTO":"Ortopedia","PEDIATRIA":"Pediatria","PED":"Pediatria",
     "NEUROLOGIA":"Neurologia","NEURO":"Neurologia"}
CAN={"APP":"APP","APLICATIVO":"APP","MOBILE":"APP","SITE":"SITE","WEB":"SITE","PORTAL":"SITE",
     "TELEFONE":"TELEFONE","PHONE":"TELEFONE","CALL":"TELEFONE","PRESENCIAL":"PRESENCIAL",
     "BALCAO":"PRESENCIAL","BALCÃO":"PRESENCIAL","FRONTDESK":"PRESENCIAL"}

def parse_date(v):
    for f in ("%Y-%m-%d","%d/%m/%Y","%d-%m-%Y","%m/%d/%Y"):
        try:return datetime.strptime(v.strip(),f).date()
        except ValueError:pass
    raise ValueError(v)

def value(v):
    s=v.strip().replace("R$","").replace(" ","")
    if "," in s and "." in s:s=s.replace(".","").replace(",",".")
    elif "," in s:s=s.replace(",",".")
    return float(s)

def dg(v):return "".join(re.findall(r"\d+",v))
def p_id(v):return f"P{int(dg(v)):06d}"
def u_id(v):return f"U{int(dg(v)):03d}"
def m_id(v):return f"M{int(dg(v)):04d}"

def age(n,r):
    return r.year-n.year-((r.month,r.day)<(n.month,n.day))

def faixa(i):
    if i<=17:return "0-17"
    if i<=21:return "18-21"
    if i<=30:return "22-30"
    if i<=45:return "31-45"
    if i<=60:return "46-60"
    return "61+"

def normalize(ag,pac,un,uf,reg,sex,nasc,esp,med,dtag,dtco,hora,status,canal,tipo,valor,sistema):
    da,dc,n=parse_date(dtag),parse_date(dtco),parse_date(nasc)
    return {
      "agendamento_id":ag.strip(),"paciente_id":p_id(pac),"unidade_id":u_id(un),
      "estado_unidade":uf.strip().upper(),"regiao_unidade":reg.strip().title(),
      "sexo":SEX.get(sex.strip().upper(),sex.strip().upper()),
      "faixa_etaria":faixa(age(n,dc)),
      "especialidade":ESP.get(esp.strip().upper(),esp.strip().title()),
      "profissional_id":m_id(med),"data_agendamento":da.isoformat(),"data_consulta":dc.isoformat(),
      "hora_consulta":hora.strip(),
      "status":STA.get(status.strip().upper().replace(" ","_"),status.strip().upper()),
      "canal_agendamento":CAN.get(canal.strip().upper(),canal.strip().upper()),
      "tipo_consulta":tipo.strip().upper().replace(" ","_"),
      "valor_consulta":f"{value(valor):.2f}",
      "dias_antecedencia":(dc-da).days,"no_shows_anteriores":0,"sistema_origem":sistema
    }

def read(path):
    with path.open(encoding="utf-8",newline="") as f:return list(csv.DictReader(f))

rows=[]
for r in read(ORIGEM/"sistema_a.csv"):
    rows.append(normalize(r["appointment_id"],r["patient_id"],r["clinic_id"],r["state"],r["region"],
    r["sex"],r["birth_date"],r["specialty"],r["doctor_id"],r["created_at"],r["appointment_date"],
    r["appointment_time"],r["status"],r["channel"],r["consultation_type"],r["price"],"SISTEMA_A"))

for r in read(ORIGEM/"sistema_b.csv"):
    rows.append(normalize(r["id_agendamento"],r["id_paciente"],r["unidade"],r["uf"],r["regiao"],
    r["genero"],r["nascimento"],r["especialidade"],r["medico"],r["dt_marcacao"],r["dt_consulta"],
    r["horario"],r["situacao"],r["origem_agendamento"],r["tipo"],r["valor"],"SISTEMA_B"))

for r in read(ORIGEM/"sistema_c.csv"):
    rows.append(normalize(r["booking"],r["patient"],r["branch"],r["uf"],r["macro_region"],
    r["gender"],r["dob"],r["service"],r["provider"],r["booked_on"],r["visit_date"],
    r["visit_time"],r["visit_status"],r["booking_channel"],r["visit_type"],r["amount"],"SISTEMA_C"))

# Deduplicação
uniq={}
for r in rows:uniq.setdefault(r["agendamento_id"],r)
rows=list(uniq.values())

# Histórico anterior por paciente
rows.sort(key=lambda r:(r["data_consulta"],r["agendamento_id"]))
hist={}
for r in rows:
    r["no_shows_anteriores"]=hist.get(r["paciente_id"],0)
    if r["status"]=="NO_SHOW":hist[r["paciente_id"]]=hist.get(r["paciente_id"],0)+1

rows.sort(key=lambda r:r["agendamento_id"])

with (OUT/"agendamentos.csv").open("w",encoding="utf-8",newline="") as f:
    w=csv.DictWriter(f,fieldnames=COLS)
    w.writeheader();w.writerows(rows)

print(f"Trusted criado: {len(rows)} registros.")
print("Grão: 1 linha = 1 agendamento de consulta.")
