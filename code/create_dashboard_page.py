#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GIA 프로젝트 통합 대시보드 메인 페이지 생성 스크립트
작성일: 2025년 8월 18일
작성자: 서대리 (Lead Developer)
목적: 과업지시서 V1.2에 따른 2단계 대시보드 프로토타입 구현
"""

import requests
import json
from datetime import datetime

# 노션 API 설정
NOTION_TOKEN = ""
PARENT_PAGE_ID = "227a613d-25ff-800c-a97d-e24f6eb521a8"  # 조대표님 워크스페이스 페이지 ID

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def create_dashboard_page():
    """대시보드 메인 페이지 생성"""
    url = "https://api.notion.com/v1/pages"
    
    # 대시보드 페이지 내용 구성
    children = [
        # 1. 상단 네비게이션 바
        {
            "object": "block",
            "type": "heading_1",
            "heading_1": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "GIA 프로젝트 통합 대시보드"
                        }
                    }
                ]
            }
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "🏠 홈 | 📈 프로젝트 대시보드 | 📂 지식 아카이브 | ⚙️ 설정"
                        }
                    }
                ]
            }
        },
        {
            "object": "block",
            "type": "divider",
            "divider": {}
        },
        
        # 2. 최근 프로젝트 활동 알림
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "최근 프로젝트 활동 알림"
                        }
                    }
                ]
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "✅ 한진중공업 프로젝트 Phase 0 완료! 다음 단계로 진행하시겠습니까?"
                        }
                    }
                ]
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "⚠️ 효성중공업 프로젝트 데이터 수집 중... 30% 진행 (서대리)"
                        }
                    }
                ]
            }
        },
        {
            "object": "block",
            "type": "divider",
            "divider": {}
        },
        
        # 3. 진행 중인 프로젝트 목록 (Gallery View)
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "진행 중인 프로젝트 목록"
                        }
                    }
                ]
            }
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "📋 조사 대상 기업 DB를 Gallery View로 연결하여 프로젝트 카드 형태로 표시"
                        }
                    }
                ]
            }
        },
        {
            "object": "block",
            "type": "divider",
            "divider": {}
        },
        
        # 4. 전체 프로젝트 현황
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "전체 프로젝트 현황"
                        }
                    }
                ]
            }
        },
        {
            "object": "block",
            "type": "column_list",
            "column_list": {
                "children": [
                    {
                        "object": "block",
                        "type": "column",
                        "column": {
                            "children": [
                                {
                                    "object": "block",
                                    "type": "heading_3",
                                    "heading_3": {
                                        "rich_text": [
                                            {
                                                "type": "text",
                                                "text": {
                                                    "content": "진행률 요약"
                                                }
                                            }
                                        ]
                                    }
                                },
                                {
                                    "object": "block",
                                    "type": "paragraph",
                                    "paragraph": {
                                        "rich_text": [
                                            {
                                                "type": "text",
                                                "text": {
                                                    "content": "• 총 3개 프로젝트 중 2개 완료\n• 현재 진행률 75%\n• 예상 완료일: 8/7"
                                                }
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "object": "block",
                        "type": "column",
                        "column": {
                            "children": [
                                {
                                    "object": "block",
                                    "type": "heading_3",
                                    "heading_3": {
                                        "rich_text": [
                                            {
                                                "type": "text",
                                                "text": {
                                                    "content": "핵심 인사이트 요약"
                                                }
                                            }
                                        ]
                                    }
                                },
                                {
                                    "object": "block",
                                    "type": "paragraph",
                                    "paragraph": {
                                        "rich_text": [
                                            {
                                                "type": "text",
                                                "text": {
                                                    "content": "• 두산: 해외 원전 특화 보험 제안\n• 효성: 신재생 에너지 기술 보험\n• [버튼] 종합 보고서 보기"
                                                }
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "object": "block",
                        "type": "column",
                        "column": {
                            "children": [
                                {
                                    "object": "block",
                                    "type": "heading_3",
                                    "heading_3": {
                                        "rich_text": [
                                            {
                                                "type": "text",
                                                "text": {
                                                    "content": "다음 실행할 작업"
                                                }
                                            }
                                        ]
                                    }
                                },
                                {
                                    "object": "block",
                                    "type": "paragraph",
                                    "paragraph": {
                                        "rich_text": [
                                            {
                                                "type": "text",
                                                "text": {
                                                    "content": "• 한진중공업 DB 생성 재개\n• 서대리 작업 결과 확인\n• [버튼] 서대리 작업 지시하기"
                                                }
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        },
        {
            "object": "block",
            "type": "divider",
            "divider": {}
        },
        
        # 5. GIA 지식 라이브러리
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "GIA 지식 라이브러리"
                        }
                    }
                ]
            }
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "📚 생성된 보고서/전략 DB를 Table View로 연결하여 최근 업데이트된 문서 목록 표시"
                        }
                    }
                ]
            }
        }
    ]
    
    payload = {
        "parent": {
            "page_id": PARENT_PAGE_ID
        },
        "properties": {
            "title": [
                {
                    "type": "text",
                    "text": {
                        "content": "GIA 프로젝트 통합 대시보드"
                    }
                }
            ]
        },
        "children": children
    }
    
    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        
        result = response.json()
        page_id = result["id"]
        
        print(f"✅ 대시보드 메인 페이지 생성 성공!")
        print(f"📋 페이지 ID: {page_id}")
        print(f"📋 페이지 URL: {result.get('url', 'N/A')}")
        
        # 페이지 ID를 파일에 저장
        with open('dashboard_page_id.txt', 'w') as f:
            f.write(page_id)
        
        return page_id
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 페이지 생성 실패: {e}")
        return None

def main():
    """메인 실행 함수"""
    print("🚀 2단계: 대시보드 페이지 UI/UX 프로토타입 구현 시작...")
    print("=" * 60)
    
    # 대시보드 메인 페이지 생성
    dashboard_page_id = create_dashboard_page()
    
    if dashboard_page_id:
        print(f"\n🎉 대시보드 메인 페이지 생성 완료!")
        print(f"📋 페이지 ID: {dashboard_page_id}")
        print(f"\n📝 다음 단계: DB 연결 및 Gallery/Table View 구현")
    else:
        print(f"\n❌ 대시보드 메인 페이지 생성 실패.")

if __name__ == "__main__":
    main()
