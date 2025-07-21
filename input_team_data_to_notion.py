#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
팀원 데이터 노션 DB 입력 스크립트
작성일: 2025년 7월 19일
목적: 시대리, 채팀장, 고과장 데이터를 노션 DB에 입력
"""

import requests
import json
import time
from datetime import datetime

# 노션 API 설정
NOTION_TOKEN = "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"

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def load_db_ids():
    """DB ID 로드"""
    try:
        with open('hyosung_dbs_created_20250719_003144.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ DB ID 파일을 찾을 수 없습니다.")
        return {}

def create_notion_page(db_id, properties):
    """노션 페이지 생성"""
    url = "https://api.notion.com/v1/pages"
    
    payload = {
        "parent": {"database_id": db_id},
        "properties": properties
    }
    
    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        
        result = response.json()
        page_id = result["id"]
        
        return page_id
        
    except requests.exceptions.RequestException as e:
        error_msg = f"페이지 생성 실패: {e}"
        if hasattr(e, 'response') and e.response is not None:
            error_msg += f" - 응답: {e.response.text}"
        print(f"❌ {error_msg}")
        return None

def input_sidari_data(db_ids):
    """시대리 데이터 입력"""
    print("\n📊 시대리 데이터 입력 시작")
    print("-" * 40)
    
    success_count = 0
    error_count = 0
    
    # 1. 기업 재무 및 프로젝트 DB (미국 수주 프로젝트)
    if "기업 재무 및 프로젝트 DB" in db_ids:
        db_id = db_ids["기업 재무 및 프로젝트 DB"]["id"]
        
        sidari_projects = [
            {
                "항목명": "LA 태양광 ESS",
                "데이터 유형": "프로젝트",
                "수치값": 120000000,
                "단위": "달러",
                "기준일": "2023-09-18",
                "사업 부문": "중공업",
                "지역": "미주",
                "중요도": "매우중요",
                "데이터 소스": "https://www.hyosunghi.com"
            },
            {
                "항목명": "텍사스 HVDC",
                "데이터 유형": "프로젝트",
                "수치값": 210000000,
                "단위": "달러",
                "기준일": "2023-12-05",
                "사업 부문": "중공업",
                "지역": "미주",
                "중요도": "매우중요",
                "데이터 소스": "https://www.hyosunghi.com"
            },
            {
                "항목명": "뉴욕 배터리팩",
                "데이터 유형": "프로젝트",
                "수치값": 90000000,
                "단위": "달러",
                "기준일": "2022-11-20",
                "사업 부문": "중공업",
                "지역": "미주",
                "중요도": "중요",
                "데이터 소스": "https://www.hyosunghi.com"
            }
        ]
        
        for project in sidari_projects:
            properties = {
                "항목명": {"title": [{"text": {"content": project["항목명"]}}]},
                "데이터 유형": {"select": {"name": project["데이터 유형"]}},
                "수치값": {"number": project["수치값"]},
                "단위": {"select": {"name": project["단위"]}},
                "기준일": {"date": {"start": project["기준일"]}},
                "사업 부문": {"multi_select": [{"name": dept} for dept in project["사업 부문"].split(',')]},
                "지역": {"select": {"name": project["지역"]}},
                "중요도": {"select": {"name": project["중요도"]}},
                "데이터 소스": {"url": project["데이터 소스"]}
            }
            
            page_id = create_notion_page(db_id, properties)
            if page_id:
                success_count += 1
                print(f"  ✅ {project['항목명']} 입력 성공")
            else:
                error_count += 1
                print(f"  ❌ {project['항목명']} 입력 실패")
            
            time.sleep(1)
    
    # 2. 신재생에너지 프로젝트 DB
    if "신재생에너지 프로젝트 DB" in db_ids:
        db_id = db_ids["신재생에너지 프로젝트 DB"]["id"]
        
        sidari_renewable = [
            {
                "프로젝트명": "새만금 태양광",
                "프로젝트 유형": "태양광",
                "프로젝트 규모": 300,
                "단위": "MW",
                "지역": "국내",
                "진행 상태": "완료",
                "시작일": "2022-10-01",
                "완료일": "2024-05-30",
                "효성중공업 역할": "변압기, 인버터",
                "계약 금액": 1500,
                "리스크 등급": "보통",
                "데이터 소스": "https://www.hyosunghi.com"
            },
            {
                "프로젝트명": "제주 해상풍력",
                "프로젝트 유형": "풍력",
                "프로젝트 규모": 200,
                "단위": "MW",
                "지역": "국내",
                "진행 상태": "진행중",
                "시작일": "2023-04-15",
                "완료일": "",
                "효성중공업 역할": "변압기, 건설",
                "계약 금액": 2200,
                "리스크 등급": "보통",
                "데이터 소스": "https://www.hyosunghi.com"
            },
            {
                "프로젝트명": "강릉 수소플랜트",
                "프로젝트 유형": "수소",
                "프로젝트 규모": 50,
                "단위": "MW",
                "지역": "국내",
                "진행 상태": "계획",
                "시작일": "2023-08-09",
                "완료일": "2026-03-31",
                "효성중공업 역할": "변압기, 인버터",
                "계약 금액": 800,
                "리스크 등급": "낮음",
                "데이터 소스": "https://www.hyosunghi.com"
            }
        ]
        
        for project in sidari_renewable:
            properties = {
                "프로젝트명": {"title": [{"text": {"content": project["프로젝트명"]}}]},
                "프로젝트 유형": {"select": {"name": project["프로젝트 유형"]}},
                "프로젝트 규모": {"number": project["프로젝트 규모"]},
                "단위": {"select": {"name": project["단위"]}},
                "지역": {"select": {"name": project["지역"]}},
                "진행 상태": {"select": {"name": project["진행 상태"]}},
                "시작일": {"date": {"start": project["시작일"]}},
                "효성중공업 역할": {"multi_select": [{"name": role} for role in project["효성중공업 역할"].split(',')]},
                "계약 금액": {"number": project["계약 금액"]},
                "리스크 등급": {"select": {"name": project["리스크 등급"]}},
                "데이터 소스": {"url": project["데이터 소스"]}
            }
            
            if project["완료일"]:
                properties["완료일"] = {"date": {"start": project["완료일"]}}
            
            page_id = create_notion_page(db_id, properties)
            if page_id:
                success_count += 1
                print(f"  ✅ {project['프로젝트명']} 입력 성공")
            else:
                error_count += 1
                print(f"  ❌ {project['프로젝트명']} 입력 실패")
            
            time.sleep(1)
    
    # 3. 정부 정책 DB
    if "정부 정책 DB" in db_ids:
        db_id = db_ids["정부 정책 DB"]["id"]
        
        sidari_policies = [
            {
                "정책명": "데이터센터 집적화 지원",
                "정책 분야": "제조업",
                "발표 기관": "과학기술정보통신부",
                "발표일": "2024-06-20",
                "시행일": "2024-06-20",
                "정책 내용": "수도권 집적화 허용 및 각종 세제 지원",
                "효성중공업 영향": "긍정",
                "관련 사업부": "중공업, TNS",
                "정책 우선순위": "우선",
                "관련 링크": "https://www.motie.go.kr"
            },
            {
                "정책명": "친환경 데이터센터 투자 유도",
                "정책 분야": "신재생에너지",
                "발표 기관": "산업통상자원부",
                "발표일": "2024-10-05",
                "시행일": "2024-10-05",
                "정책 내용": "그린에너지 매칭 조건부 투자 인센티브, PPA 우선 지원",
                "효성중공업 영향": "긍정",
                "관련 사업부": "중공업, TNS",
                "정책 우선순위": "우선",
                "관련 링크": "https://www.motie.go.kr"
            },
            {
                "정책명": "지역상생 데이터 인프라 확충",
                "정책 분야": "제조업",
                "발표 기관": "행정안전부",
                "발표일": "2025-03-17",
                "시행일": "2025-03-17",
                "정책 내용": "비수도권 신규 클라우드/데이터센터 설립에 대한 금융지원 확대",
                "효성중공업 영향": "긍정",
                "관련 사업부": "중공업, TNS",
                "정책 우선순위": "보통",
                "관련 링크": "https://www.moef.go.kr"
            }
        ]
        
        for policy in sidari_policies:
            properties = {
                "정책명": {"title": [{"text": {"content": policy["정책명"]}}]},
                "정책 분야": {"select": {"name": policy["정책 분야"]}},
                "발표 기관": {"select": {"name": policy["발표 기관"]}},
                "발표일": {"date": {"start": policy["발표일"]}},
                "시행일": {"date": {"start": policy["시행일"]}},
                "정책 내용": {"rich_text": [{"text": {"content": policy["정책 내용"]}}]},
                "효성중공업 영향": {"select": {"name": policy["효성중공업 영향"]}},
                "관련 사업부": {"multi_select": [{"name": dept} for dept in policy["관련 사업부"].split(',')]},
                "정책 우선순위": {"select": {"name": policy["정책 우선순위"]}},
                "관련 링크": {"url": policy["관련 링크"]}
            }
            
            page_id = create_notion_page(db_id, properties)
            if page_id:
                success_count += 1
                print(f"  ✅ {policy['정책명']} 입력 성공")
            else:
                error_count += 1
                print(f"  ❌ {policy['정책명']} 입력 실패")
            
            time.sleep(1)
    
    print(f"\n📊 시대리 데이터 입력 완료:")
    print(f"  ✅ 성공: {success_count}건")
    print(f"  ❌ 실패: {error_count}건")
    
    return success_count, error_count

def input_chateam_data(db_ids):
    """채팀장 데이터 입력"""
    print("\n📊 채팀장 데이터 입력 시작")
    print("-" * 40)
    
    success_count = 0
    error_count = 0
    
    # 1. 핵심 인물 DB
    if "핵심 인물 DB" in db_ids:
        db_id = db_ids["핵심 인물 DB"]["id"]
        
        chateam_person = {
            "인물명": "우태희",
            "직책": "대표이사",
            "소속 부문": "지주회사",
            "담당 영역": "경영총괄, 기술개발, 해외사업",
            "경력": "1962년 출생. 배문고 졸업, 연세대 행정학과 학사, 서울대 행정대학원 행정학 석사, UC 버클리 경제정책학 석사, 경희대 경영학 박사 학위 취득. 제27회 행정고시(1983년) 합격 후 통상산업부 등에서 통상 관료로 근무, 산업자원부 차관, 산업통상자원부 2차관(2016년) 역임. 연세대 특임교수, 한국에너지공단 자문역, 대한상의 상근부회장(2020~2024) 등 민간·학계 활동 후, 2024년 2월 효성중공업 대표이사로 선임.",
            "학력": "연세대학교 행정학과, 서울대학교 행정대학원, UC 버클리 경제정책학 석사, 경희대학교 경영학 박사",
            "주요 성과": "우태희 사장은 HVDC(고압직류송전), ESS(에너지저장장치) 등 미래형 전력기술을 확장하여 효성중공업을 글로벌 최고 수준의 전력기기 공급사로 만들겠다는 비전을 제시했다. 실제로 효성중공업은 200MW급 전압형 HVDC 변환장치 개발에 성공했으며, 세계적인 송전망 확충 수요를 타고 관련 수주가 확대되고 있다.",
            "중요도": "매우중요"
        }
        
        properties = {
            "인물명": {"title": [{"text": {"content": chateam_person["인물명"]}}]},
            "직책": {"select": {"name": chateam_person["직책"]}},
            "소속 부문": {"select": {"name": chateam_person["소속 부문"]}},
            "담당 영역": {"multi_select": [{"name": area} for area in chateam_person["담당 영역"].split(',')]},
            "경력": {"rich_text": [{"text": {"content": chateam_person["경력"]}}]},
            "학력": {"rich_text": [{"text": {"content": chateam_person["학력"]}}]},
            "주요 성과": {"rich_text": [{"text": {"content": chateam_person["주요 성과"]}}]},
            "중요도": {"select": {"name": chateam_person["중요도"]}}
        }
        
        page_id = create_notion_page(db_id, properties)
        if page_id:
            success_count += 1
            print(f"  ✅ {chateam_person['인물명']} 입력 성공")
        else:
            error_count += 1
            print(f"  ❌ {chateam_person['인물명']} 입력 실패")
        
        time.sleep(1)
    
    # 2. 정부 정책 DB (추가)
    if "정부 정책 DB" in db_ids:
        db_id = db_ids["정부 정책 DB"]["id"]
        
        chateam_policies = [
            {
                "정책명": "U자형 에너지 고속도로 구축 (재생에너지 전환 정책)",
                "정책 분야": "신재생에너지",
                "발표 기관": "산업통상자원부",
                "발표일": "2025-06-01",
                "시행일": "2025-06-01",
                "정책 내용": "2030년까지 서해안, 2040년까지 한반도 전역을 잇는 'U자형 에너지 고속도로'(초고압 직류송전 HVDC 및 육상 송전망)를 구축하여 재생에너지 전환을 가속화한다. 이를 위해 분산형 지능형 전력망(AI·빅데이터 활용) 구축, ESS 설치를 통한 RE100 산업단지 조성, 그린수소 생산 확대 등 기반 인프라 강화를 추진한다.",
                "효성중공업 영향": "긍정",
                "관련 사업부": "중공업, TNS",
                "정책 우선순위": "최우선",
                "관련 링크": "https://blog.haezoom.com/notice_11/"
            },
            {
                "정책명": "원자력·SMR 개발 및 해외시장 진출 지원",
                "정책 분야": "제조업",
                "발표 기관": "산업통상자원부",
                "발표일": "2025-01-01",
                "시행일": "2025-01-01",
                "정책 내용": "이재명 정부의 국정과제에는 '차세대 원전 개발', '소형원전(SMR) 육성', '해외 원전시장 개척'이 명시되어 있다. 이에 따라 국내 원전 건설 재개와 함께 원전 수출 활성화 정책(해외 원전 인허가 지원, 금융지원 등)이 추진될 전망이다.",
                "효성중공업 영향": "긍정",
                "관련 사업부": "중공업",
                "정책 우선순위": "우선",
                "관련 링크": "https://edata.ekn.kr/article/view/ekn202506120002"
            }
        ]
        
        for policy in chateam_policies:
            properties = {
                "정책명": {"title": [{"text": {"content": policy["정책명"]}}]},
                "정책 분야": {"select": {"name": policy["정책 분야"]}},
                "발표 기관": {"select": {"name": policy["발표 기관"]}},
                "발표일": {"date": {"start": policy["발표일"]}},
                "시행일": {"date": {"start": policy["시행일"]}},
                "정책 내용": {"rich_text": [{"text": {"content": policy["정책 내용"]}}]},
                "효성중공업 영향": {"select": {"name": policy["효성중공업 영향"]}},
                "관련 사업부": {"multi_select": [{"name": dept} for dept in policy["관련 사업부"].split(',')]},
                "정책 우선순위": {"select": {"name": policy["정책 우선순위"]}},
                "관련 링크": {"url": policy["관련 링크"]}
            }
            
            page_id = create_notion_page(db_id, properties)
            if page_id:
                success_count += 1
                print(f"  ✅ {policy['정책명']} 입력 성공")
            else:
                error_count += 1
                print(f"  ❌ {policy['정책명']} 입력 실패")
            
            time.sleep(1)
    
    # 3. 글로벌 보험중개 시장 DB
    if "글로벌 보험중개 시장 DB" in db_ids:
        db_id = db_ids["글로벌 보험중개 시장 DB"]["id"]
        
        chateam_insurance = [
            {
                "회사명": "Marsh & McLennan Companies, Inc.",
                "회사 유형": "글로벌 보험중개사",
                "본사 위치": "미국",
                "연매출": 230000,
                "직원 수": 85000,
                "주요 서비스": "기업보험, 리스크관리, 컨설팅, 재보험",
                "효성중공업 경쟁력": "열세",
                "특화 영역": "전력, 건설, 제조",
                "록톤과의 관계": "경쟁사",
                "분석 메모": "전 세계적 네트워크와 다양한 리스크 관리·보험 중개 서비스를 제공. 디지털 전환과 데이터 분석 기반 솔루션 제공으로 혁신적 경쟁력 보유.",
                "데이터 소스": "https://www.xprimm.com/AM-Best%E2%80%99s-Top-20-Global-Brokers-2024-Marsh-McLennan-and-Aon-top-the-ranking-for-the-14th-consecutive-year-articol-124-22006.htm"
            },
            {
                "회사명": "Aon plc",
                "회사 유형": "글로벌 보험중개사",
                "본사 위치": "영국",
                "연매출": 120000,
                "직원 수": 50000,
                "주요 서비스": "기업보험, 재보험, 컨설팅, 퇴직연금",
                "효성중공업 경쟁력": "동등",
                "특화 영역": "제조, IT, 금융",
                "록톤과의 관계": "경쟁사",
                "분석 메모": "광범위한 데이터 분석 역량과 글로벌 네트워크를 활용해 미래 위험을 예측·관리. 보험·퇴직연금·건강관리 전 영역에서 종합 솔루션 제공.",
                "데이터 소스": "https://www.xprimm.com/AM-Best%E2%80%99s-Top-20-Global-Brokers-2024-Marsh-McLennan-and-Aon-top-the-ranking-for-the-14th-consecutive-year-articol-124-22006.htm"
            },
            {
                "회사명": "Willis Towers Watson PLC",
                "회사 유형": "글로벌 보험중개사",
                "본사 위치": "영국",
                "연매출": 90000,
                "직원 수": 45000,
                "주요 서비스": "리스크 자문, HR 컨설팅, 데이터 분석",
                "효성중공업 경쟁력": "동등",
                "특화 영역": "IT, 금융, 건설",
                "록톤과의 관계": "경쟁사",
                "분석 메모": "폭넓은 사업 범위와 고도화된 컨설팅 역량. 첨단 분석 툴 및 기후리스크 솔루션 제공. 전 세계적으로 다양한 리스크 자문·중개 서비스를 보유.",
                "데이터 소스": "https://insurtechdigital.com/top10/top-10-insurance-brokers"
            }
        ]
        
        for company in chateam_insurance:
            properties = {
                "회사명": {"title": [{"text": {"content": company["회사명"]}}]},
                "회사 유형": {"select": {"name": company["회사 유형"]}},
                "본사 위치": {"select": {"name": company["본사 위치"]}},
                "연매출": {"number": company["연매출"]},
                "직원 수": {"number": company["직원 수"]},
                "주요 서비스": {"multi_select": [{"name": service} for service in company["주요 서비스"].split(',')]},
                "효성중공업 경쟁력": {"select": {"name": company["효성중공업 경쟁력"]}},
                "특화 영역": {"multi_select": [{"name": area} for area in company["특화 영역"].split(',')]},
                "록톤과의 관계": {"select": {"name": company["록톤과의 관계"]}},
                "분석 메모": {"rich_text": [{"text": {"content": company["분석 메모"]}}]},
                "데이터 소스": {"url": company["데이터 소스"]}
            }
            
            page_id = create_notion_page(db_id, properties)
            if page_id:
                success_count += 1
                print(f"  ✅ {company['회사명']} 입력 성공")
            else:
                error_count += 1
                print(f"  ❌ {company['회사명']} 입력 실패")
            
            time.sleep(1)
    
    print(f"\n📊 채팀장 데이터 입력 완료:")
    print(f"  ✅ 성공: {success_count}건")
    print(f"  ❌ 실패: {error_count}건")
    
    return success_count, error_count

def input_gojang_data(db_ids):
    """고과장 데이터 입력"""
    print("\n📊 고과장 데이터 입력 시작")
    print("-" * 40)
    
    success_count = 0
    error_count = 0
    
    # 1. 핵심 인물 DB (요약)
    if "핵심 인물 DB" in db_ids:
        db_id = db_ids["핵심 인물 DB"]["id"]
        
        gojang_person = {
            "인물명": "우태희",
            "직책": "대표이사",
            "소속 부문": "지주회사",
            "담당 영역": "경영총괄, 기술개발",
            "경력": "前 산업통상자원부 차관; 現 효성중공업 대표이사. 산업부 재직 시 신재생에너지 정책 주도(2030 온실가스 감축·ESS 보급 확대); 기고문·강연(ESG·탄소중립); 대표 취임 후 수소·풍력·ESS 신사업 진두지휘",
            "학력": "연세대학교 행정학과, 서울대학교 행정대학원",
            "주요 성과": "글로벌 전력인프라·수소 시장 선도하여 탄소 없는 에너지 시대 개척. 북미·유럽 수주 1조원 이상 확대; 데이터센터 전력인프라 솔루션 개발 주도; 정부·기업 정책 가교 역할",
            "중요도": "매우중요"
        }
        
        properties = {
            "인물명": {"title": [{"text": {"content": gojang_person["인물명"]}}]},
            "직책": {"select": {"name": gojang_person["직책"]}},
            "소속 부문": {"select": {"name": gojang_person["소속 부문"]}},
            "담당 영역": {"multi_select": [{"name": area} for area in gojang_person["담당 영역"].split(',')]},
            "경력": {"rich_text": [{"text": {"content": gojang_person["경력"]}}]},
            "학력": {"rich_text": [{"text": {"content": gojang_person["학력"]}}]},
            "주요 성과": {"rich_text": [{"text": {"content": gojang_person["주요 성과"]}}]},
            "중요도": {"select": {"name": gojang_person["중요도"]}}
        }
        
        page_id = create_notion_page(db_id, properties)
        if page_id:
            success_count += 1
            print(f"  ✅ {gojang_person['인물명']} (요약) 입력 성공")
        else:
            error_count += 1
            print(f"  ❌ {gojang_person['인물명']} (요약) 입력 실패")
        
        time.sleep(1)
    
    # 2. 정부 정책 DB (요약)
    if "정부 정책 DB" in db_ids:
        db_id = db_ids["정부 정책 DB"]["id"]
        
        gojang_policies = [
            {
                "정책명": "이재명 정부 해외 진출 지원 정책",
                "정책 분야": "무역",
                "발표 기관": "산업통상자원부",
                "발표일": "2025-03-01",
                "시행일": "2025-03-01",
                "정책 내용": "수출 금융·보증 프로그램 확대; 해외 투자 인센티브(세제·융자); 외교적 지원 강화(MOU 체결 지원)",
                "효성중공업 영향": "긍정",
                "관련 사업부": "중공업, TNS",
                "정책 우선순위": "우선",
                "관련 링크": "https://www.motie.go.kr"
            },
            {
                "정책명": "이재명 정부 신재생에너지 확대 정책",
                "정책 분야": "신재생에너지",
                "발표 기관": "산업통상자원부",
                "발표일": "2025-04-01",
                "시행일": "2025-04-01",
                "정책 내용": "발전 설비 보조금 확대; 2030년 재생비중 30% 목표; 인허가 절차 원스톱 간소화; ESS·수소 R&D 지원",
                "효성중공업 영향": "긍정",
                "관련 사업부": "중공업, TNS",
                "정책 우선순위": "우선",
                "관련 링크": "https://www.korea.kr"
            }
        ]
        
        for policy in gojang_policies:
            properties = {
                "정책명": {"title": [{"text": {"content": policy["정책명"]}}]},
                "정책 분야": {"select": {"name": policy["정책 분야"]}},
                "발표 기관": {"select": {"name": policy["발표 기관"]}},
                "발표일": {"date": {"start": policy["발표일"]}},
                "시행일": {"date": {"start": policy["시행일"]}},
                "정책 내용": {"rich_text": [{"text": {"content": policy["정책 내용"]}}]},
                "효성중공업 영향": {"select": {"name": policy["효성중공업 영향"]}},
                "관련 사업부": {"multi_select": [{"name": dept} for dept in policy["관련 사업부"].split(',')]},
                "정책 우선순위": {"select": {"name": policy["정책 우선순위"]}},
                "관련 링크": {"url": policy["관련 링크"]}
            }
            
            page_id = create_notion_page(db_id, properties)
            if page_id:
                success_count += 1
                print(f"  ✅ {policy['정책명']} (요약) 입력 성공")
            else:
                error_count += 1
                print(f"  ❌ {policy['정책명']} (요약) 입력 실패")
            
            time.sleep(1)
    
    # 3. 글로벌 보험중개 시장 DB (요약)
    if "글로벌 보험중개 시장 DB" in db_ids:
        db_id = db_ids["글로벌 보험중개 시장 DB"]["id"]
        
        gojang_insurance = [
            {
                "회사명": "Marsh",
                "회사 유형": "글로벌 보험중개사",
                "본사 위치": "미국",
                "연매출": 200000,
                "직원 수": 80000,
                "주요 서비스": "기업보험, 리스크관리, 컨설팅",
                "효성중공업 경쟁력": "열세",
                "특화 영역": "전력, 건설",
                "록톤과의 관계": "경쟁사",
                "분석 메모": "글로벌 네트워크, 산업별 전문성 보유. 고비용 구조가 단점.",
                "데이터 소스": "https://www.marsh.com/en/industries.html"
            },
            {
                "회사명": "Aon",
                "회사 유형": "글로벌 보험중개사",
                "본사 위치": "영국",
                "연매출": 120000,
                "직원 수": 50000,
                "주요 서비스": "기업보험, 재보험, 컨설팅",
                "효성중공업 경쟁력": "동등",
                "특화 영역": "제조, IT",
                "록톤과의 관계": "경쟁사",
                "분석 메모": "리스크 모델링 기술, ESG 솔루션 강점. 일부 지역 서비스 부족.",
                "데이터 소스": "https://www.aon.com/home"
            },
            {
                "회사명": "WTW",
                "회사 유형": "글로벌 보험중개사",
                "본사 위치": "영국",
                "연매출": 90000,
                "직원 수": 45000,
                "주요 서비스": "리스크 자문, HR 컨설팅",
                "효성중공업 경쟁력": "동등",
                "특화 영역": "건설, 제조",
                "록톤과의 관계": "경쟁사",
                "분석 메모": "컨설팅 통합 서비스, 리서치 역량 강점. 기술 기반 약함.",
                "데이터 소스": "https://www.wtwco.com/industries.html"
            }
        ]
        
        for company in gojang_insurance:
            properties = {
                "회사명": {"title": [{"text": {"content": company["회사명"]}}]},
                "회사 유형": {"select": {"name": company["회사 유형"]}},
                "본사 위치": {"select": {"name": company["본사 위치"]}},
                "연매출": {"number": company["연매출"]},
                "직원 수": {"number": company["직원 수"]},
                "주요 서비스": {"multi_select": [{"name": service} for service in company["주요 서비스"].split(',')]},
                "효성중공업 경쟁력": {"select": {"name": company["효성중공업 경쟁력"]}},
                "특화 영역": {"multi_select": [{"name": area} for area in company["특화 영역"].split(',')]},
                "록톤과의 관계": {"select": {"name": company["록톤과의 관계"]}},
                "분석 메모": {"rich_text": [{"text": {"content": company["분석 메모"]}}]},
                "데이터 소스": {"url": company["데이터 소스"]}
            }
            
            page_id = create_notion_page(db_id, properties)
            if page_id:
                success_count += 1
                print(f"  ✅ {company['회사명']} (요약) 입력 성공")
            else:
                error_count += 1
                print(f"  ❌ {company['회사명']} (요약) 입력 실패")
            
            time.sleep(1)
    
    print(f"\n📊 고과장 데이터 입력 완료:")
    print(f"  ✅ 성공: {success_count}건")
    print(f"  ❌ 실패: {error_count}건")
    
    return success_count, error_count

def main():
    """메인 실행 함수"""
    print("=" * 80)
    print("🚀 팀원 데이터 노션 DB 입력 시작")
    print("=" * 80)
    
    # DB ID 로드
    db_ids = load_db_ids()
    if not db_ids:
        print("❌ DB ID를 로드할 수 없습니다.")
        return
    
    print(f"✅ {len(db_ids)}개 DB ID 로드 완료")
    
    # 시대리 데이터 입력
    sidari_success, sidari_error = input_sidari_data(db_ids)
    
    # 채팀장 데이터 입력
    chateam_success, chateam_error = input_chateam_data(db_ids)
    
    # 고과장 데이터 입력
    gojang_success, gojang_error = input_gojang_data(db_ids)
    
    # 전체 결과 요약
    total_success = sidari_success + chateam_success + gojang_success
    total_error = sidari_error + chateam_error + gojang_error
    
    print("\n" + "=" * 80)
    print("📊 전체 입력 결과 요약")
    print("=" * 80)
    print(f"✅ 총 성공: {total_success}건")
    print(f"❌ 총 실패: {total_error}건")
    print(f"📈 성공률: {(total_success / (total_success + total_error) * 100):.1f}%" if (total_success + total_error) > 0 else "📈 성공률: 0%")
    
    if total_error == 0:
        print("\n🎉 모든 데이터 입력 완료!")
    else:
        print(f"\n⚠️ {total_error}건의 입력 실패가 있습니다.")
    
    return total_success, total_error

if __name__ == "__main__":
    main() 