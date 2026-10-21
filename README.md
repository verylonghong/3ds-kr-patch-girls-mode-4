# 걸스 모드 4 한국어 패치 0.7

일본판 **Girls Mode 4 - Star & Stylist**의 한국어 패치입니다.

- 배포 버전: **0.7**
- 한글화: **롱홍**
- 대상 타이틀 ID: `000400000019F600`

## 반영 내용

- 번역 메시지 71,203개를 반영했습니다.
- 나눔스퀘어라운드 기반 한글 글꼴 6개를 반영했습니다.
- 이미지 505개의 한글화·보정을 반영했습니다.

## 0.7 변경 요약

- 1인칭 표현과 호칭, 문장 조사를 정리했습니다.
- 이름·브랜드명 뒤 조사 자동 선택을 적용했습니다.
- 중복된 「스타일」 표현을 정리하고 헤어스타일링·펌·미용사·엔·주황색 등의 용어를 통일했습니다.
- 어색한 표현과 반복, 메일·스토리 안내의 줄바꿈을 보정했습니다.
- UI 이미지 26개의 글자 크기·위치, 버튼·테두리·배경과 잔여 픽셀을 보정했습니다.

[패치 파일 SHA-256](SHA256SUMS.txt)

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

[버전 0.7 릴리스](https://github.com/verylonghong/3ds-kr-patch-girls-mode-4/releases/tag/v0.7)에서 다음 두 가지 패치를 제공합니다.

| 파일 | 용도 | 크기 |
| --- | --- | ---: |
| `GS4_Korean_v0.7_From_Japan_3DS.xdelta` | 지정한 원본 `.3ds`에 적용 | 9,606,314바이트 |
| `GS4_Korean_Repack_v0.7.zip` | RomFS·ExeFS 교체 후 재패킹 | 59,526,201바이트 |

## 기준 원본과 SHA-256

### xdelta 기준 원본

파일명: `Girls Mode 4 - Star & Stylist (Japan).3ds`

파일 크기: **1,073,741,824바이트**

```text
c4e36a941c183633d93d7df40b10b23616dc0092334477c4b1d28264714e3b30
```

xdelta는 원본의 내용이 위 해시와 일치해야 합니다.

PowerShell에서 확인하는 명령:

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath 'Girls Mode 4 - Star & Stylist (Japan).3ds'
```

## xdelta 적용

xdelta3로 다음과 같이 적용합니다.

```powershell
xdelta3.exe -d -s "Girls Mode 4 - Star & Stylist (Japan).3ds" "GS4_Korean_v0.7_From_Japan_3DS.xdelta" "GS4_Korean_v0.7.3ds"
```

결과 파일은 **원본 전자설명서를 포함한 3DS 파일**입니다.

- 결과 파일명: `GS4_Korean_v0.7.3ds`
- 결과 크기: **825,430,016바이트**
- 결과 SHA-256:

```text
4fa845b8b493bef3517964a511ab93e987066b6cbb3df41e7ac39c2ce54180da
```

## 재패킹 ZIP 적용

SHA-256 값이 맞는 원본 롬을 찾기 어려울 경우 재패킹 ZIP을 적용해주세요.
ZIP에는 다음 구조의 교체 파일 **38개만** 들어 있습니다.

```text
000400000019F600/
├─ romfs/          # 번역·글꼴·이미지 교체 파일 36개
└─ exefs/
   ├─ code.bin     # 조사 선택 기능
   └─ icon.bin     # 게임 아이콘 1개
```

1. 재패킹 도구로 일본판 게임 본체의 RomFS와 ExeFS를 추출합니다.
2. `000400000019F600/romfs/`의 내용을 추출한 RomFS에 같은 상대 경로로 덮어씁니다.
3. `000400000019F600/exefs/code.bin`과 `icon.bin`을 추출한 ExeFS의 실행 파일과 아이콘에 덮어씁니다.
4. 재패킹 도구로 ExeFS·RomFS 및 CIA 또는 3DS를 다시 생성합니다.

`exefs/icon.bin`은 **재패킹용**입니다. 공식 Luma3DS의 LayeredFS 폴더에 넣는 것만으로 HOME 메뉴 아이콘이 변경되지는 않습니다.

## 글꼴 라이선스

한글 글꼴은 `NanumSquareRoundR.ttf`를 바탕으로 만든 **GS4 Korean Round** 비트맵 글꼴입니다. [SIL Open Font License 1.1](licenses/NanumSquareRound-OFL.txt)을 따릅니다. 저작권 및 변경 안내는 [FONT-NOTICE.md](FONT-NOTICE.md)에 있습니다.
