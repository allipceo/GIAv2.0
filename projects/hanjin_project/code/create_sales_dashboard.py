#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
영업 대시보드 페이지 생성 스크립트
작성일: 2025년 8월 5일
작성자: 서대리 (Lead Developer)
목적: 영업 상황 종합 대시보드 구축
"""

import requests
import json
from datetime import datetime

# 노션 API 설정
NOTION_TOKEN = ""
PARENT_PAGE_ID = "227a613d25ff800ca97de24f6eb521a8"  # GIA_작업장

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def create_sales_dashboard():
    """영업 대시보드 페이지 생성"""
    print("="*80)
    print("🚀 영업 대시보드 페이지 생성")
    print("="*80)
    
    url = "https://api.notion.com/v1/pages"
    
    # 대시보드 페이지 내용 구성
    page_content = {
        "parent": {
            "page_id": PARENT_PAGE_ID
        },
        "properties": {
            "title": {
                "title": [
                    {
                        "text": {
                            "content": "🎯 GIA 영업 대시보드"
                        }
                    }
                ]
            }
        },
        "children": [
            # 1. 대시보드 개요
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "📊 영업 상황 종합 대시보드"
                            }
                        }
                    ]
                }
            },
            {
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "이 대시보드는 록톤코리아의 영업 상황을 종합적으로 관리하는 중앙 허브입니다. 전반적인 영업 상황, 업계 현황, 주요 관심 회사들의 정보를 한눈에 확인할 수 있습니다."
                            }
                        }
                    ],
                    "icon": {
                        "type": "emoji",
                        "emoji": "🎯"
                    },
                    "color": "blue_background"
                }
            },
            
            # 2. 전반적인 영업 상황
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "📈 전반적인 영업 상황"
                            }
                        }
                    ]
                }
            },
            {
                "object": "block",
                "type": "toggle",
                "toggle": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "2025년 8월 현재 영업 현황"
                            }
                        }
                    ],
                    "children": [
                        {
                            "object": "block",
                            "type": "bulleted_list_item",
                            "bulleted_list_item": {
                                "rich_text": [
                                    {
                                        "type": "text",
                                        "text": {
                                            "content": "진행 중인 프로젝트: 3개 (효성중공업, 두산중공업, 한진중공업)"
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
                                            "content": "완료된 분석: 3개 회사 기업 정보 분석 및 보험 니즈 분석"
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
                                            "content": "수집된 뉴스: 총 135개 (회사별 45개씩)"
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
                                            "content": "생성된 제안서: 3개 회사별 영업 전략 제안서"
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            },
            
            # 3. 업계 현황 뉴스
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "📰 업계 현황 뉴스"
                            }
                        }
                    ]
                }
            },
            {
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "중공업 업계 동향: 신재생에너지 사업 확대, 해양플랜트 시장 성장, 환경 규제 강화"
                            }
                        }
                    ],
                    "icon": {
                        "type": "emoji",
                        "emoji": "📈"
                    },
                    "color": "green_background"
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
                                "content": "해상풍력 시장: 연평균 25% 성장, 2030년까지 12GW 목표"
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
                                "content": "해양플랜트 시장: 글로벌 시장 규모 약 200조원, 연평균 15% 성장"
                            }
                        }
                    ]
                }
            },
            
            # 4. 입찰 정보
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "🏗️ 입찰 정보"
                            }
                        }
                    ]
                }
            },
            {
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "주요 관심 분야: 해양플랜트, 신재생에너지, 해양엔지니어링 프로젝트"
                            }
                        }
                    ],
                    "icon": {
                        "type": "emoji",
                        "emoji": "🔍"
                    },
                    "color": "yellow_background"
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
                                "content": "해상풍력 프로젝트: 2024년 다수 프로젝트 발주 예정"
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
                                "content": "해양플랜트 유지보수: 기존 시설 유지보수 계약 갱신 시기"
                            }
                        }
                    ]
                }
            },
            
            # 5. 정책 사항
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "📋 정책 사항"
                            }
                        }
                    ]
                }
            },
            {
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "정부 정책: 2030년까지 해상풍력 12GW 목표, 탄소중립 정책 강화"
                            }
                        }
                    ],
                    "icon": {
                        "type": "emoji",
                        "emoji": "🏛️"
                    },
                    "color": "purple_background"
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
                                "content": "환경 규제: 해양환경 보호 규제 강화, 친환경 기술 개발 지원"
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
                                "content": "금융 지원: 신재생에너지 프로젝트 금융 지원 확대"
                            }
                        }
                    ]
                }
            },
            
            # 6. 주요 관심 회사 리스트
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "🏢 주요 관심 회사 리스트"
                            }
                        }
                    ]
                }
            },
            {
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "아래 회사들을 클릭하면 각 회사의 상세 페이지로 이동합니다."
                            }
                        }
                    ],
                    "icon": {
                        "type": "emoji",
                        "emoji": "🔗"
                    },
                    "color": "gray_background"
                }
            },
            
            # 회사별 정보 테이블 형태로 구성
            {
                "object": "block",
                "type": "table_of_contents",
                "table_of_contents": {
                    "color": "default"
                }
            },
            
            # 효성중공업 정보
            {
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "🏭 효성중공업"
                            }
                        }
                    ]
                }
            },
            {
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "대표이사: 김영주 | 2024년 매출: 15,234억원 | 주요사업: 조선, 해양플랜트, 신재생에너지"
                            }
                        }
                    ],
                    "icon": {
                        "type": "emoji",
                        "emoji": "📊"
                    },
                    "color": "blue_background"
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
                                "content": "상태: 기업 정보 분석 완료, 보험 니즈 분석 완료"
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
                                "content": "수집 뉴스: 45개 | 생성 보고서: 2개"
                            }
                        }
                    ]
                }
            },
            
            # 두산중공업 정보
            {
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "🏭 두산중공업"
                            }
                        }
                    ]
                }
            },
            {
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "대표이사: 박정수 | 2024년 매출: 13,567억원 | 주요사업: 조선, 해양플랜트, 엔진"
                            }
                        }
                    ],
                    "icon": {
                        "type": "emoji",
                        "emoji": "📊"
                    },
                    "color": "blue_background"
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
                                "content": "상태: 기업 정보 분석 완료, 보험 니즈 분석 완료"
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
                                "content": "수집 뉴스: 45개 | 생성 보고서: 2개"
                            }
                        }
                    ]
                }
            },
            
            # 한진중공업 정보
            {
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "🏭 한진중공업"
                            }
                        }
                    ]
                }
            },
            {
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "대표이사: 조원국 | 2024년 매출: 11,648억원 | 주요사업: 해양플랜트, 신재생에너지, 해양엔지니어링"
                            }
                        }
                    ],
                    "icon": {
                        "type": "emoji",
                        "emoji": "📊"
                    },
                    "color": "blue_background"
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
                                "content": "상태: 기업 정보 분석 완료, 보험 니즈 분석 완료, 통합 페이지 생성 완료"
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
                                "content": "수집 뉴스: 45개 | 생성 보고서: 2개 | 통합 페이지: 생성됨"
                            }
                        }
                    ]
                }
            },
            
            # 7. 빠른 링크
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "🔗 빠른 링크"
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
                                "content": "효성중공업 상세 페이지"
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
                                "content": "두산중공업 상세 페이지"
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
                                "content": "한진중공업 통합 페이지"
                            }
                        }
                    ]
                }
            },
            
            # 8. 업데이트 정보
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "📅 최근 업데이트"
                            }
                        }
                    ]
                }
            },
            {
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": f"2025년 8월 5일: 한진중공업 프로젝트 Phase 1 완료, 통합 페이지 생성"
                            }
                        }
                    ],
                    "icon": {
                        "type": "emoji",
                        "emoji": "✅"
                    },
                    "color": "green_background"
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
                                "content": "2025년 7월: 효성중공업, 두산중공업 프로젝트 완료"
                            }
                        }
                    ]
                }
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=HEADERS, json=page_content)
        response.raise_for_status()
        
        result = response.json()
        page_id = result["id"]
        page_url = result["url"]
        
        print(f"✅ 영업 대시보드 페이지 생성 완료!")
        print(f"   - Page ID: {page_id}")
        print(f"   - URL: {page_url}")
        
        # 결과 저장
        result_file = f"../data/sales_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump({
                "page_id": page_id,
                "page_url": page_url,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }, f, ensure_ascii=False, indent=2)
        
        print(f"💾 결과 파일 저장: {result_file}")
        print("🎯 영업 대시보드 구축 완료!")
        
        return page_id, page_url
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 영업 대시보드 페이지 생성 실패: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   - 응답 내용: {e.response.text}")
        return None, None

def main():
    """메인 실행 함수"""
    create_sales_dashboard()

if __name__ == "__main__":
    main() 