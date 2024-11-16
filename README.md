💡 서비스 개요
Hiro, we are hiring! 하이로는 채용담당관의 요구사항을 기반으로 적합한 이력서를 추천해주는 서비스입니다.
많은 이력서들 중에 채용 담당관이 원하는 이력서를 더 쉽고 빠르게 찾을 수 있도록 돕고자 만들었습니다. 

💡 개요
잘못된 정보와 가짜 뉴스는 사회적 혼란, 정치적 불안정, 경제적 손실, 공공 건강 위협, 교육 저하, 법적 문제를 유발합니다. 이 서비스는 이러한 사회적 문제를 해결하기 위해 정확한 정보를 제공하여 여러분이 올바른 결정을 내릴 수 있도록 돕기 위해 개발되었습니다.

🕹️ 배경
수많은 이력서 속에서 채용담당관이 원하는 인재를 찾는 일은 쉽지 않습니다.

💻 애플리케이션 소개
목적: 사용자가 입력한 정보를 바탕으로 사실 여부를 확인하고 검증합니다.
주요 기능:
사실 확인: 입력된 텍스트의 사실 여부를 분석합니다.
출처 제공: 검증된 정보의 출처를 제공합니다.
역사적 사실 검증: 역사적 사건이나 인물에 대한 정보를 확인합니다.
실시간 업데이트: 최신 정보를 반영하여 사실 여부를 확인합니다.

💡 Getting Started
```
sh build.sh
```

💡 API 명세
```
# FastAPI 앱 구동 후 동작
http://localhost:8000/docs
```

스크린샷



스크린샷

🛠 기술 스택
FastAPI, LangChain, Chroma, OpenAI
💎 개발자
신은성	임요한
profile	profile
watanka	obov


Author
See our CODEOWNERS file.


💻 Release
docker 컨테이너 형식으로 AWS EC2에 배포하였고, github action으로 CI/CD 파이프라인을 구현하였습니다.

https://fact-checker-fe.vercel.app/
[발표자료](./pdf/FactChecker팀 최종 발표 c87df5402c4d4e77819f95b63e7227aa.pdf)

📝 License
This project is MIT licensed.

