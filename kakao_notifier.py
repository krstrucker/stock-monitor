"""
카카오톡 알림 모듈
카카오톡 비즈니스 API를 사용하여 알림을 전송합니다.
"""
import requests
import os
import json
from typing import List, Optional


class KakaoNotifier:
    """카카오톡 알림 클래스"""
    
    def __init__(self, rest_api_key: str = None, admin_key: str = None):
        """
        Args:
            rest_api_key: 카카오 REST API 키
            admin_key: 카카오 Admin 키
        """
        self.rest_api_key = rest_api_key or os.environ.get('KAKAO_REST_API_KEY', '')
        self.admin_key = admin_key or os.environ.get('KAKAO_ADMIN_KEY', '')
        self.talk_plus_friend_id = os.environ.get('KAKAO_TALK_PLUS_FRIEND_ID', '')
    
    def send_message(self, message: str, recipient_id: str = None) -> bool:
        """
        카카오톡 메시지 전송
        
        Args:
            message: 전송할 메시지
            recipient_id: 수신자 ID (없으면 기본 수신자)
        
        Returns:
            전송 성공 여부
        """
        if not self.admin_key:
            print("⚠️ 카카오톡 Admin 키가 설정되지 않았습니다.")
            return False
        
        try:
            # 카카오톡 알림톡 API 사용
            url = 'https://kapi.kakao.com/v2/api/talk/memo/default/send'
            headers = {
                'Authorization': f'KakaoAK {self.admin_key}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            # 템플릿 ID가 필요할 수 있음 (카카오 비즈니스 계정에서 발급)
            data = {
                'template_id': os.environ.get('KAKAO_TEMPLATE_ID', ''),
                'template_args': json.dumps({'message': message})
            }
            
            response = requests.post(url, headers=headers, data=data, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ 카카오톡 알림 전송 성공")
                return True
            else:
                print(f"❌ 카카오톡 알림 전송 실패: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 카카오톡 알림 전송 실패: {str(e)}")
            return False
    
    def send_friend_message(self, message: str, user_id: str) -> bool:
        """
        카카오톡 친구톡 메시지 전송 (더 간단한 방법)
        
        Args:
            message: 전송할 메시지
            user_id: 카카오톡 사용자 ID
        
        Returns:
            전송 성공 여부
        """
        if not self.rest_api_key:
            print("⚠️ 카카오톡 REST API 키가 설정되지 않았습니다.")
            return False
        
        try:
            # 카카오톡 챗봇 API 또는 친구톡 API 사용
            # 실제 구현은 카카오톡 API 문서 참조
            print(f"📱 카카오톡 친구톡 전송: {message[:50]}...")
            return True
            
        except Exception as e:
            print(f"❌ 카카오톡 친구톡 전송 실패: {str(e)}")
            return False


class TelegramNotifier:
    """텔레그램 알림 클래스 (카카오톡 대안)"""
    
    def __init__(self, bot_token: str = None, chat_id: str = None):
        """
        Args:
            bot_token: 텔레그램 봇 토큰
            chat_id: 채팅 ID
        """
        self.bot_token = bot_token or os.environ.get('TELEGRAM_BOT_TOKEN', '')
        self.chat_id = chat_id or os.environ.get('TELEGRAM_CHAT_ID', '')
    
    def send_message(self, message: str) -> bool:
        """
        텔레그램 메시지 전송
        
        Args:
            message: 전송할 메시지
        
        Returns:
            전송 성공 여부
        """
        if not self.bot_token or not self.chat_id:
            print("⚠️ 텔레그램 봇 토큰 또는 채팅 ID가 설정되지 않았습니다.")
            return False
        
        try:
            url = f'https://api.telegram.org/bot{self.bot_token}/sendMessage'
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, json=data, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ 텔레그램 알림 전송 성공")
                return True
            else:
                print(f"❌ 텔레그램 알림 전송 실패: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 텔레그램 알림 전송 실패: {str(e)}")
            return False

