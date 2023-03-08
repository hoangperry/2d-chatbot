import requests


if __name__ == '__main__':
    url = 'https://vbee.vn/api/v1/tts'

    payload = {
        'voice_code': 'sg_female_lantrinh_vdts_48k-fhg',
        'speed_rate': '1.0',
        'input_text': 'Nhóm nghiên cứu tại Đại học Oxford phát triển hệ thống nhận dạng giọng nói đa ngôn ngữ tên là Whisper bằng phương pháp tiền huấn luyện và không giám sát. Họ đã đề xuất phương pháp mới WhisperX để giải quyết vấn đề nhận dạng âm thanh dài hạn với ba bước bổ sung để cải thiện độ chính xác của dữ liệu thời gian',
        'app_id': 'b1201881-7579-419f-9eb6-7b5e192ac7b5',
        'callback_url': 'https://shopai.vn/a',
    }
    headers = {
        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE2NzgxODIxNjd9.dv0kO4YmKTXlvgbjMH9kvkruOFtnIumLGbsLqj_iFjs',
    }

    response = requests.request('POST', url, data=payload, headers=headers)

    print(response.text)

