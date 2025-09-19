from playwright.sync_api import sync_playwright
# Playwright의 "동기(sync) API"를 불러옴.
# → sync_playwright()를 쓰면 with 블록 안에서 브라우저 자동 실행/종료가 가능해짐.

def analyze_dom(url: str):
    # 웹사이트의 DOM 구조를 분석하는 함수 정의 (매개변수 url: 분석할 웹 주소)

    with sync_playwright() as p:
        # Playwright 실행 환경을 열고, 종료 시 자동으로 정리됨 (컨텍스트 매니저 패턴)

        browser = p.chromium.launch(headless=False)  
        # 크로미움(Chrome 엔진 기반 브라우저)을 실행
        # headless=False → 실제 브라우저 창을 띄워서 동작을 눈으로 볼 수 있음
        # headless=True → 화면은 띄우지 않고 백그라운드에서 실행됨

        page = browser.new_page()
        # 새 탭(브라우저 페이지) 하나 생성                                  ==> browser 하나 띄워서 그 URL로 이동
        page.goto(url)
        # 지정된 URL로 이동 (네트워크 요청 발생 → 페이지 로딩)

        print("\n===== FRAME 구조 확인 =====")
        # 현재 페이지 안에 어떤 frame(iframe, frameset 포함)이 있는지 확인

        for frame in page.frames:
            print("FRAME:", frame.name, frame.url)
        # page.frames → 페이지 안에 존재하는 모든 프레임(최상위 + iframe들)을 리스트로 반환
        # frame.name: 프레임 이름
        # frame.url: 해당 프레임이 로드한 실제 URL

        # 🔹 우선 최상위 DOM에서 시도
        print("\n===== 최상위 DOM 요소 =====")

        try:
            page.wait_for_selector("input, button, a, form", timeout=5000)
            # 페이지 최상위 DOM에서 input, button, a, form 태그 중 하나라도 나타날 때까지 기다림 (최대 5초)
            # → 동적 로딩되는 사이트에서 "아직 요소가 안 떠서 못 잡는 상황"을 방지

        except:
            print("⚠️ 최상위 DOM에서 바로 안 잡힘 (프레임 가능성 높음)")
            # 만약 5초 안에 못 찾으면 예외 발생 → 보통은 iframe 안에 있는 경우

        print_dom_elements(page)                                    ## 여기선 최상위 구조에서 확인.
        # 최상위 DOM(page)에서 input/button/link/form 속성을 출력

        # 🔹 프레임 내부 탐색
        for frame in page.frames:
            if frame.url != page.url:  
                # 자기 자신(최상위 프레임)은 제외하고, 자식 프레임(iframe 등)만 탐색

                print(f"\n===== 프레임 탐색: {frame.name} ({frame.url}) =====")

                try:
                    frame.wait_for_selector("input, button, a, form", timeout=5000)
                    # 프레임 안에서 input/button/a/form이 나타날 때까지 기다림
                except:
                    print("⚠️ 프레임에서도 요소 대기 실패")
                    # 해당 프레임에 요소가 없거나, 로딩이 늦어서 못 잡은 경우

                print_dom_elements(frame)
                # 프레임 내부 DOM 요소들을 출력                 ****iframe 에 있는 요소확인

        browser.close()
        # 브라우저 종료 (창 닫기)


def print_dom_elements(scope):
    """input / button / link / form 속성을 보기 좋게 출력"""
    # scope 매개변수: page 또는 frame 객체
    # 이 함수는 입력된 범위(scope) 안에서 input, button, link, form 태그들을 모두 찾아 속성을 출력함

    # INPUT
    inputs = scope.locator("input")
    # locator("input") → 현재 scope(page/frame) 안의 모든 input 요소를 참조
    # locator는 게으른 평가(lazy evaluation) 방식 → count()나 nth()를 호출할 때 실제 DOM 탐색 수행

    for i in range(inputs.count()):
        # inputs.count() → input 요소 개수
        # nth(i) → i번째 input 요소
        el = inputs.nth(i)
        print(f"[INPUT {i}]",
              "type=", el.get_attribute("type"),             # input 타입 (text, password, hidden 등)
              "id=", el.get_attribute("id"),                 # id 속성
              "name=", el.get_attribute("name"),             # name 속성
              "placeholder=", el.get_attribute("placeholder"), # placeholder (아이디/비밀번호 같은 안내 문구)
              "class=", el.get_attribute("class"),           # class 속성
              "required=", el.get_attribute("required"),     # 필수 입력 여부
              "maxlength=", el.get_attribute("maxlength"),   # 최대 입력 글자 수
              "pattern=", el.get_attribute("pattern"),       # 정규식 입력 패턴
              "disabled=", el.get_attribute("disabled"))     # 비활성화 여부

    # BUTTON
    buttons = scope.locator("button, input[type='submit'], input[type='button']")
    # button 태그 뿐만 아니라, input 태그 중 type이 submit 또는 button인 것도 버튼으로 간주해서 수집

    for i in range(buttons.count()):
        el = buttons.nth(i)
        print(f"[BUTTON {i}]",
              "text=", el.inner_text(),                     # 버튼 안의 보이는 텍스트
              "type=", el.get_attribute("type"),            # 버튼 타입 (submit, reset, button 등)
              "id=", el.get_attribute("id"),                # id 속성
              "class=", el.get_attribute("class"),          # class 속성
              "disabled=", el.get_attribute("disabled"))    # 버튼 비활성화 여부

    # LINK
    links = scope.locator("a")
    # a 태그(하이퍼링크) 전부 탐색

    for i in range(links.count()):
        el = links.nth(i)
        print(f"[LINK {i}]",
              "text=", el.inner_text(),                     # 링크에 보이는 텍스트
              "href=", el.get_attribute("href"),            # 이동할 주소
              "target=", el.get_attribute("target"))        # 새창(_blank) 여부 등

    # FORM
    forms = scope.locator("form")
    # form 태그(데이터 제출용 폼) 전부 탐색

    for i in range(forms.count()):
        el = forms.nth(i)
        print(f"[FORM {i}]",
              "action=", el.get_attribute("action"),        # form 전송 대상 URL
              "method=", el.get_attribute("method"),        # form 전송 방식 (GET/POST)
              "id=", el.get_attribute("id"),                # id 속성
              "class=", el.get_attribute("class"))          # class 속성


if __name__ == "__main__":
    analyze_dom("https://portal.inu.ac.kr:444/enview/")
    # 프로그램 진입점: 실행하면 analyze_dom()을 호출해서 인천대 포털 사이트의 DOM 분석 시작
