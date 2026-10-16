# 걸스 모드 4 한국어 패치 0.5

일본판 대상 한국어 패치입니다. xdelta와 재패킹 교체 파일 두 가지를 배포합니다.

- `GS4_Korean_v0.5_From_Japan_3DS.xdelta` — 약 4.55MiB
- `GS4_Korean_Repack_v0.5.zip` — 약 12.37MiB

기준 `.3ds`: `Girls Mode 4 - Star & Stylist (Japan).3ds` (1,073,741,824바이트)

```text
SHA-256: c4e36a941c183633d93d7df40b10b23616dc0092334477c4b1d28264714e3b30
```

### xdelta 패치 적용 결과

- 파일명: `GS4_Korean_v0.5_WithManual.3ds`
- 파일 크기: **824,578,048바이트**
- SHA-256:

```text
fa4c698f0a8f69c2da99e993d0352aecb3118746cc7f6f61271d6a6d1a8946e3
```

번역 71,203개, 한글 글꼴 6개와 한글화·보정 이미지 491개를 반영했습니다. xdelta 적용 결과에는 원본 전자설명서와 파티션 6·7이 포함됩니다. 재패킹 ZIP은 `000400000019F600/` 아래에 RomFS 교체 파일 33개와 `exefs/icon.bin`만 포함합니다.

xdelta 복원 결과의 SHA-256 일치와 재패킹 파일 해시를 검증했습니다. 게임 실행 검사는 하지 않았습니다.

기준 원본 해시, 적용 방법과 글꼴 라이선스는 [README](https://github.com/verylonghong/3ds-kr-patch-girls-mode-4#readme)를 확인하세요.
