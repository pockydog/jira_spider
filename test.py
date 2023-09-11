import requests


def api_response_time(api_url):
    try:
        response = requests.get(api_url, timeout=5)  # 設定超時時間為5秒
        response.raise_for_status()  # 如果狀態碼不是200，這將引發HTTPError
        return response.elapsed.total_seconds()
    except requests.RequestException as e:  # 捕獲所有requests異常
        print(f"Error occurred: {e}")
        return float('inf')  # 返回無窮大，確保測試失敗


def test_api_response_within_threshold(api_url="https://www.taiwanlottery.com.tw/agencyap/agencyap_instant_login.aspx",
                                       threshold=1):
    response_time = api_response_time(api_url)

    # 列印相關資訊
    print(f"\nAPI URL: {api_url}")
    print(f"Response Time: {response_time:.4f} seconds")
    # 使用assert來判定回應時間是否超過閾值
    assert response_time <= threshold, f"API response time exceeded {threshold} seconds threshold"
