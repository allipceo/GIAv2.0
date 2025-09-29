#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
한진중공업 통합 페이지 생성 스크립트
작성일: 2025년 8월 5일
작성자: 서대리 (Lead Developer)
목적: 한진중공업의 모든 정보를 통합한 노션 페이지 생성
"""

import requests
import json
from datetime import datetime

# 노션 API 설정
NOTION_TOKEN = "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"
PARENT_PAGE_ID = "227a613d25ff800ca97de24f6eb521a8"  # GIA_작업장

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def create_hanjin_integrated_page():
    """한진중공업 통합 페이지 생성"""
    print("="*80)
    print("🚀 한진중공업 통합 페이지 생성")
    print("="*80)
    
    url = "https://api.notion.com/v1/pages"
    
    # 페이지 내용 구성
    page_content = {
        "parent": {
            "page_id": PARENT_PAGE_ID
        },
        "properties": {
            "title": {
                "title": [
                    {
                        "text": {
                            "content": "한진중공업 (HJ중공업) - 통합 영업 전략 페이지"
                        }
                    }
                ]
            }
        },
        "children": [
            # 1. 기본 정보 섹션
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "🏢 한진중공업 기본 정보"
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
                                "content": "대표이사: 조원국 | 2024년 매출: 11,648억원 | 직원수: 약 3,000명"
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
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "주요 사업: 해양플랜트 70%, 신재생에너지 20%, 해양엔지니어링 10%"
                            }
                        }
                    ]
                }
            },
            
            # 2. 최신 뉴스 섹션
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "📰 최신 뉴스 (45개 수집됨)"
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
                                "content": "2025년 8월 5일 기준, 9개 키워드로 45개 뉴스 수집 완료"
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
            
            # 3. 기업 분석 섹션
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "📈 기업 분석"
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
                                "content": "사업 영역 분석"
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
                                            "content": "해양플랜트: 국내 시장점유율 1위, 연평균 15% 성장"
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
                                            "content": "신재생에너지: 2024년 2,000억원 투자, 2030년까지 5GW 목표"
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            },
            
            # 4. 보험 니즈 섹션
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "🛡️ 보험 니즈 분석"
                            }
                        }
                    ]
                }
            },
            {
                "object": "block",
                "type": "numbered_list_item",
                "numbered_list_item": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "건설공사보험: 대형 해양플랜트 프로젝트 (예상보험료: 프로젝트 규모의 1-2%)"
                            }
                        }
                    ]
                }
            },
            {
                "object": "block",
                "type": "numbered_list_item",
                "numbered_list_item": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "기계보험: 고가의 해양플랜트 장비 (예상보험료: 장비가치의 0.5-1%)"
                            }
                        }
                    ]
                }
            },
            
            # 5. 영업 전략 섹션
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "🎯 록톤코리아 영업 전략"
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
                                "content": "핵심 제안: 프로젝트별 맞춤 보험 설계 + 리스크 관리 파트너십 + 글로벌 네트워크 활용"
                            }
                        }
                    ],
                    "icon": {
                        "type": "emoji",
                        "emoji": "💡"
                    },
                    "color": "yellow_background"
                }
            },
            
            # 6. 보고서 링크 섹션
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "📋 관련 보고서"
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
                                "content": "한진중공업_보험중개_영업전략_제안서_V1.0.md"
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
                                "content": "한진중공업_프로젝트_Phase1_완료보고서.md"
                            }
                        }
                    ]
                }
            },
            
            # 7. 관계형 DB 연결 정보
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "🔗 연결된 데이터베이스"
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
                                "content": "회사 정보 마스터 DB, 기업재무 및 프로젝트 DB, 기업위험 프로파일 DB, 핵심인물 DB와 연결됨"
                            }
                        }
                    ],
                    "icon": {
                        "type": "emoji",
                        "emoji": "🔗"
                    },
                    "color": "purple_background"
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
        
        print(f"✅ 한진중공업 통합 페이지 생성 완료!")
        print(f"   - Page ID: {page_id}")
        print(f"   - URL: {page_url}")
        
        # 결과 저장
        result_file = f"../data/hanjin_integrated_page_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump({
                "page_id": page_id,
                "page_url": page_url,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }, f, ensure_ascii=False, indent=2)
        
        print(f"💾 결과 파일 저장: {result_file}")
        print("🎯 한진중공업 통합 페이지 생성 완료!")
        
        return page_id, page_url
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 한진중공업 통합 페이지 생성 실패: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   - 응답 내용: {e.response.text}")
        return None, None

def main():
    """메인 실행 함수"""
    create_hanjin_integrated_page()

if __name__ == "__main__":
    main() 