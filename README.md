# 걸스 모드 4 한국어 패치 0.5

일본판 **Girls Mode 4 - Star & Stylist**의 한국어 패치입니다.

- 배포 버전: **0.5**
- 한글화: **롱홍**
- 대상 타이틀 ID: `000400000019F600`

## 반영 내용

- 번역 메시지 71,203개를 반영했습니다.
- 나눔스퀘어라운드 기반 한글 글꼴 6개를 반영했습니다.
- 이미지 491개의 한글화·보정을 반영했습니다.
- 인명·용어·오탈자 검수에서 승인된 수정과 고객 메모의 표현·줄 나누기를 반영했습니다.
- 음식 이름 `라멘` 13곳을 `라면`으로, `仕入・仕入れ`를 `매입`으로 번역한 12곳을 `사입`으로 통일했습니다.
- 상점의 `사입하러 가기` 버튼, 날짜 전환 요일과 일정 버튼의 글자색·외곽선을 보정했습니다.
- 게임 아이콘을 반영했습니다. 게임 실행 코드 `code.bin`은 변경하지 않았습니다.

## 스크린샷

<p align="center">
  <img src="screenshots/gm4_01.png" width="400" alt="게임 화면 1">
  <img src="screenshots/gm4_02.png" width="400" alt="게임 화면 2">
</p>
<p align="center">
  <img src="screenshots/gm4_03.png" width="400" alt="게임 화면 3">
  <img src="screenshots/gm4_04.png" width="400" alt="게임 화면 4">
</p>

## 다운로드

[버전 0.5 릴리스](https://github.com/verylonghong/3ds-kr-patch-girls-mode-4/releases/tag/v0.5)에서 다음 두 가지 패치를 제공합니다.

| 파일 | 용도 | 크기 |
| --- | --- | ---: |
| `GS4_Korean_v0.5_From_Japan_3DS.xdelta` | 지정한 원본 `.3ds`에 적용 | 4,769,398바이트 |
| `GS4_Korean_Repack_v0.5.zip` | RomFS·ExeFS 교체 후 재패킹 | 12,972,252바이트 |

## 기준 원본과 SHA-256

### xdelta 기준 원본

파일명: `Girls Mode 4 - Star & Stylist (Japan).3ds`

파일 크기: **1,073,741,824바이트**

```text
c4e36a941c183633d93d7df40b10b23616dc0092334477c4b1d28264714e3b30
```

xdelta는 파일명뿐 아니라 원본의 내용도 위 해시와 일치해야 합니다.

PowerShell에서 확인하는 명령:

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath 'Girls Mode 4 - Star & Stylist (Japan).3ds'
```

### 재패킹 교체분 검증에 사용한 일본판 CIA

파일명: `Girls Mode 4 (J).cia`

파일 크기: **762,291,200바이트**

```text
0929b225e4deffa0ae2794a47b00e3e40295e64bf2760ac18f3866a0a002a710
```

재패킹 ZIP은 파일 교체 방식이며, xdelta의 기준 원본은 위의 `.3ds`입니다.

## xdelta 적용

xdelta3로 다음과 같이 적용합니다.

```powershell
xdelta3.exe -d -s "Girls Mode 4 - Star & Stylist (Japan).3ds" "GS4_Korean_v0.5_From_Japan_3DS.xdelta" "GS4_Korean_v0.5_WithManual.3ds"
```

결과 파일은 **전자설명서와 원본 파티션 6·7을 포함한 3DS 파일**입니다.

- 결과 파일명: `GS4_Korean_v0.5_WithManual.3ds`
- 결과 크기: **824,578,048바이트**
- 결과 SHA-256:

```text
fa4c698f0a8f69c2da99e993d0352aecb3118746cc7f6f61271d6a6d1a8946e3
```

## 재패킹 ZIP 적용

ZIP에는 다음 구조의 교체 파일 **34개만** 들어 있습니다.

```text
000400000019F600/
├─ romfs/          # 번역·글꼴·이미지 교체 파일 33개
└─ exefs/
   └─ icon.bin     # 게임 아이콘 1개
```

1. 재패킹 도구로 일본판 게임 본체의 RomFS와 ExeFS를 추출합니다.
2. `000400000019F600/romfs/`의 내용을 추출한 RomFS에 같은 상대 경로로 덮어씁니다.
3. `000400000019F600/exefs/icon.bin`을 추출한 ExeFS의 아이콘에 덮어씁니다. 도구에서 `icon` 또는 `icon.icn`이라는 파일명을 사용한다면 해당 이름에 맞춥니다.
4. 재패킹 도구로 ExeFS·RomFS 및 CIA 또는 3DS를 다시 생성합니다. 아이콘 교체에 따른 검증 해시와 CIA 메타데이터도 갱신합니다.

게임 실행 코드·배너·ExHeader는 원본을 사용합니다. 전자설명서의 포함 여부는 재패킹 도구에서 선택합니다.

`exefs/icon.bin`은 **재패킹용**입니다. 공식 Luma3DS의 LayeredFS 폴더에 넣는 것만으로 HOME 메뉴 아이콘이 변경되지는 않습니다.

## 검증 기록

- 정적 검사 19개와 3DS의 게임 데이터 해시·RomFS 119개 파일 대조를 통과했습니다.
- xdelta를 기준 원본에 적용한 결과가 빌드한 3DS 파일과 SHA-256까지 일치함을 확인했습니다.
- 재패킹 ZIP의 교체 파일 34개를 검증된 파일 및 해시와 대조했습니다.
- 버전 0.5의 게임 실행 검사는 하지 않았습니다.

배포 파일의 SHA-256은 [SHA256SUMS.txt](SHA256SUMS.txt)에 기록했습니다.

## 글꼴 라이선스

한글 글꼴은 `NanumSquareRoundR.ttf`를 바탕으로 만든 **GS4 Korean Round** 비트맵 글꼴입니다. [SIL Open Font License 1.1](licenses/NanumSquareRound-OFL.txt)을 따릅니다. 저작권 및 변경 안내는 [FONT-NOTICE.md](FONT-NOTICE.md)에 있습니다.
