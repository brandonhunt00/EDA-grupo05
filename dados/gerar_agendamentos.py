#!/usr/bin/env python3
import argparse, csv, random
from datetime import date, timedelta
from pathlib import Path

BASE = Path(__file__).resolve().parent
OUT = BASE / "origem"

ESPECIALIDADES = {
    "Cardiologia": ["Cardiologia","CARDIOLOGIA","Cardio","CARD"],
    "Dermatologia": ["Dermatologia","DERMATOLOGIA","Derma"],
    "Ortopedia": ["Ortopedia","ORTOPEDIA","Orto"],
    "Pediatria": ["Pediatria","PEDIATRIA","Ped"],
    "Neurologia": ["Neurologia","NEUROLOGIA","Neuro"],
}
CANAIS = {
    "APP": ["APP","app","Aplicativo","mobile"],
    "SITE": ["SITE","site","WEB","Portal"],
    "TELEFONE": ["TELEFONE","Telefone","phone","CALL"],
    "PRESENCIAL": ["PRESENCIAL","Balcao","BALCÃO","frontdesk"],
}
STATUS = {
    "REALIZADO": ["REALIZADO","Realizado","DONE","ATENDIDO"],
    "NO_SHOW": ["NO_SHOW","No-Show","no_show","FALTOU","AUSENTE"],
    "CANCELADO": ["CANCELADO","Cancelado","CANCELLED"],
    "AGENDADO": ["AGENDADO","Agendado","SCHEDULED"],
    "CONFIRMADO": ["CONFIRMADO","Confirmado","CONFIRMED"],
}
SEXO = {
    "MASCULINO": ["M","Masculino","masculino","MALE","Masc"],
    "FEMININO": ["F","Feminino","feminino","FEMALE","Fem"],
}
UNIDADES = [
    ("U001","PE","Nordeste"),("U002","BA","Nordeste"),("U003","CE","Nordeste"),
    ("U004","SP","Sudeste"),("U005","RJ","Sudeste"),("U006","MG","Sudeste"),
    ("U007","PR","Sul"),("U008","RS","Sul"),("U009","GO","Centro-Oeste"),("U010","DF","Centro-Oeste"),
]
VALORES = {
    "Cardiologia":(220,420),"Dermatologia":(160,320),"Ortopedia":(200,380),
    "Pediatria":(140,280),"Neurologia":(260,480)
}

def prob_no_show(idade, sexo, mes, canal, historico, antecedencia):
    p = 0.08
    if 22 <= idade <= 30: p += 0.05
    if sexo == "MASCULINO": p += 0.015
    if mes in (7,12): p += 0.04
    if canal == "APP": p += 0.015
    if historico > 0: p += min(0.08, historico*0.02)
    if antecedencia >= 30: p += 0.02
    return min(p, 0.40)

def data_fmt(d, sistema, rng):
    if sistema == "A": return d.isoformat()
    if sistema == "B": return d.strftime(rng.choice(["%d/%m/%Y","%d-%m-%Y"]))
    return d.strftime(rng.choice(["%Y-%m-%d","%m/%d/%Y"]))

def moeda(v, sistema, rng):
    if sistema == "A": return f"{v:.2f}"
    if sistema == "B": return rng.choice([f"{v:.2f}".replace(".",","), f"R$ {v:.2f}".replace(".",","), str(round(v))])
    return f"{v:.2f}"

def uid(v, sistema):
    n=int(v[1:])
    return v if sistema=="A" else (f"Unidade {n}" if sistema=="B" else f"BRANCH-{n:03d}")

def pid(n, sistema):
    return f"P{n:06d}" if sistema=="A" else (str(n) if sistema=="B" else f"PAT-{n:06d}")

def mid(n, sistema):
    return f"M{n:04d}" if sistema=="A" else (f"MED-{n}" if sistema=="B" else f"DR{n:04d}")

def write(path, rows):
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--registros",type=int,default=10000)
    ap.add_argument("--seed",type=int,default=42)
    args=ap.parse_args()
    rng=random.Random(args.seed)
    OUT.mkdir(parents=True,exist_ok=True)

    n_pac=max(1200,args.registros//4)
    ref=date(2026,12,31)
    pacientes={}
    for n in range(1,n_pac+1):
        idade=rng.randint(1,84)
        sexo=rng.choice(["MASCULINO","FEMININO"])
        nasc=ref-timedelta(days=idade*365+rng.randint(0,364))
        pacientes[n]={"idade":idade,"sexo":sexo,"nasc":nasc,"hist":0}

    A,B,C=[],[],[]
    inicio=date(2026,1,1)

    for i in range(1,args.registros+1):
        sistema=rng.choices(["A","B","C"],weights=[.4,.35,.25])[0]
        np=rng.randint(1,n_pac)
        p=pacientes[np]
        unidade,uf,reg=rng.choice(UNIDADES)
        esp=rng.choice(list(ESPECIALIDADES))
        canal=rng.choice(list(CANAIS))
        tipo=rng.choice(["ROTINA","RETORNO","PRIMEIRA_CONSULTA"])
        dtag=inicio+timedelta(days=rng.randint(0,334))
        ant=rng.randint(1,60)
        dtco=min(dtag+timedelta(days=ant),date(2026,12,31))
        hora=f"{rng.randint(7,18):02d}:{rng.choice([0,15,30,45]):02d}"
        valor=round(rng.uniform(*VALORES[esp]),2)

        pns=prob_no_show(p["idade"],p["sexo"],dtco.month,canal,p["hist"],ant)
        x=rng.random()
        if x<pns:
            st="NO_SHOW"; p["hist"]+=1
        elif x<pns+.72: st="REALIZADO"
        elif x<pns+.82: st="CANCELADO"
        elif x<pns+.91: st="CONFIRMADO"
        else: st="AGENDADO"

        ag=f"A{i:07d}"
        med=rng.randint(1,350)

        if sistema=="A":
            A.append({
                "appointment_id":ag,"patient_id":pid(np,sistema),"clinic_id":uid(unidade,sistema),
                "state":uf,"region":reg,"sex":rng.choice(SEXO[p["sexo"]]),
                "birth_date":data_fmt(p["nasc"],sistema,rng),"specialty":rng.choice(ESPECIALIDADES[esp]),
                "doctor_id":mid(med,sistema),"created_at":data_fmt(dtag,sistema,rng),
                "appointment_date":data_fmt(dtco,sistema,rng),"appointment_time":hora,
                "status":rng.choice(STATUS[st]),"channel":rng.choice(CANAIS[canal]),
                "consultation_type":tipo,"price":moeda(valor,sistema,rng)
            })
        elif sistema=="B":
            B.append({
                "id_agendamento":ag,"id_paciente":pid(np,sistema),"unidade":uid(unidade,sistema),
                "uf":uf,"regiao":reg.lower(),"genero":rng.choice(SEXO[p["sexo"]]),
                "nascimento":data_fmt(p["nasc"],sistema,rng),"especialidade":rng.choice(ESPECIALIDADES[esp]),
                "medico":mid(med,sistema),"dt_marcacao":data_fmt(dtag,sistema,rng),
                "dt_consulta":data_fmt(dtco,sistema,rng),"horario":hora,
                "situacao":rng.choice(STATUS[st]),"origem_agendamento":rng.choice(CANAIS[canal]),
                "tipo":tipo.title(),"valor":moeda(valor,sistema,rng)
            })
        else:
            C.append({
                "booking":ag,"patient":pid(np,sistema),"branch":uid(unidade,sistema),"uf":uf,
                "macro_region":reg.upper(),"gender":rng.choice(SEXO[p["sexo"]]),
                "dob":data_fmt(p["nasc"],sistema,rng),"service":rng.choice(ESPECIALIDADES[esp]),
                "provider":mid(med,sistema),"booked_on":data_fmt(dtag,sistema,rng),
                "visit_date":data_fmt(dtco,sistema,rng),"visit_time":hora,
                "visit_status":rng.choice(STATUS[st]),"booking_channel":rng.choice(CANAIS[canal]),
                "visit_type":tipo.lower(),"amount":moeda(valor,sistema,rng)
            })

    write(OUT/"sistema_a.csv",A)
    write(OUT/"sistema_b.csv",B)
    write(OUT/"sistema_c.csv",C)
    print(f"{args.registros} registros brutos gerados.")

if __name__=="__main__":
    main()
