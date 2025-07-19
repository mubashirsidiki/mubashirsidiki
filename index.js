const thisYear = new Date().getFullYear();
const startTimeOfThisYear = new Date(`${thisYear}-01-01T00:00:00+00:00`).getTime();
const endTimeOfThisYear = new Date(`${thisYear}-12-31T23:59:59+00:00`).getTime();
const progressOfThisYear = (Date.now() - startTimeOfThisYear) / (endTimeOfThisYear - startTimeOfThisYear);
const progressBarOfThisYear = generateProgressBar();

let monthNames = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];

function generateProgressBar() {
    const progressBarCapacity = 30;
    const passedProgressBarIndex = parseInt(progressOfThisYear * progressBarCapacity);
    const progressBar = Array(progressBarCapacity)
        .fill('▁')
        .map((value, index) => index < passedProgressBarIndex ? '█' : value)
        .join('');
    return `{ ${progressBar} }`;
}

const readme = `\
# Hi there! <img src="https://github.com/TheDudeThatCode/TheDudeThatCode/blob/master/Assets/Hi.gif" width="35" />
<p align="center">
<a href="https://twitter.com/mubashirdev" target="blank"><img align="center" src="https://cdn.jsdelivr.net/npm/simple-icons@3.0.1/icons/twitter.svg" alt="twitter" height="30" width="30" /></a>&nbsp;
<a href="https://linkedin.com/in/mubashirahmedsiddiqui" target="blank"><img align="center" src="https://cdn.jsdelivr.net/npm/simple-icons@3.0.1/icons/linkedin.svg" alt="linkedin" height="30" width="30" /></a>&nbsp;
<a href="https://discord.com/users/mubashir" target="blank"><img align="center" src="https://cdn.jsdelivr.net/npm/simple-icons@3.0.1/icons/discord.svg" alt="discord" height="40" width="30" /></a>&nbsp;
<a href="https://www.buymeacoffee.com/mubashirdev"><img align="center" alt="Buy me a Coffee" width="30px" src="https://cdn.jsdelivr.net/npm/simple-icons@3.0.1/icons/buymeacoffee.svg" /></a>
</p>

![](https://media.giphy.com/media/qgQUggAC3Pfv687qPC/giphy.gif)

### <img src="https://github.com/TheDudeThatCode/TheDudeThatCode/blob/master/Assets/Developer.gif" width="45" /> About Me:
- 🧠 AI Engineer + Backend Developer working on open-source, GenAI agents, and scalable systems.
- 🏆 Winner of Traversaal x Optimized AI Hackathon, judged by Google & NVIDIA engineers.
- 🌍 Co-founder of [Hoopoes](https://github.com/hoopoes) – empowering devs through open-source collaboration.
- 💻 I use daily: **.py**, **.ts**, **.js**, **.sql**, **bash**
- ⚙️ I build with: **FastAPI**, **LangChain**, **Docker**, **Azure**, **Twilio**, **MongoDB**, **Postgres**, **React/Next.js**
- 💬 Talk to me about AI agents, OSS, community, storytelling, or cricket!
- ⚡ Fun fact: I started coding for activism, and stayed for the impact.

---

### 🧑‍💻 Tech I work on:

<p align="center">
  <img src="https://www.vectorlogo.zone/logos/python/python-icon.svg" alt="python" width="55" height="55"/>
  <img src="https://www.vectorlogo.zone/logos/fastapi/fastapi-icon.svg" alt="fastapi" width="55" height="55"/>
  <img src="https://www.vectorlogo.zone/logos/typescriptlang/typescriptlang-icon.svg" alt="ts" width="55" height="55"/>
  <img src="https://www.vectorlogo.zone/logos/docker/docker-official.svg" alt="docker" width="60" height="50"/>
  <img src="https://www.vectorlogo.zone/logos/microsoft_azure/microsoft_azure-icon.svg" alt="azure" width="55" height="55"/>
  <img src="https://www.vectorlogo.zone/logos/mongodb/mongodb-icon.svg" alt="mongodb" width="45" height="55"/>
  <img src="https://www.vectorlogo.zone/logos/postgresql/postgresql-icon.svg" alt="postgres" width="45" height="55"/>
  <img src="https://www.vectorlogo.zone/logos/reactjs/reactjs-icon.svg" alt="react" width="45" height="45"/>
  <img src="https://www.vectorlogo.zone/logos/vercel/vercel-icon.svg" alt="vercel" width="45" height="45"/>
</p>

---

### <img src='https://media1.giphy.com/media/du3J3cXyzhj75IOgvA/giphy.gif' width='25' /> My Github Stats:
![Mubashir's github stats](https://github-readme-stats.vercel.app/api?username=mubashir-dev&show_icons=true&title_color=ffc857&icon_color=8ac926&text_color=daf7dc&bg_color=151515&hide=issues&count_private=true&include_all_commits=true)
[![Top Langs](https://github-readme-stats.vercel.app/api/top-langs/?username=mubashir-dev&layout=compact&text_color=daf7dc&bg_color=151515&hide=css,html)](https://github.com/anuraghazra/github-readme-stats)
[![GitHub Streak](https://github-readme-streak-stats.herokuapp.com/?user=mubashir-dev&theme=dark)](https://git.io/streak-stats)

⏳ **Year Progress:** ${progressBarOfThisYear} ${(progressOfThisYear * 100).toFixed(2)}% as on ⏰ ${(new Date().getDate()) + '-' + monthNames[new Date().getMonth()] + '-' + new Date().getFullYear()}

---

### 🧠 My Recent Work:
<!-- BLOG-POST-LIST:START -->
- [How I Built an Open Source AI Agent with FastAPI + Twilio](https://hoopoes.dev)
- [Lessons from Winning a Google-Judged Hackathon](https://hoopoes.dev)
- [FastStart: A Fullstack Starter Template for FastAPI Developers](https://github.com/hoopoes/faststart)
<!-- BLOG-POST-LIST:END -->

▶ [... view more](https://hoopoes.dev/)

---

### 📌 A Quote I Like:
<a href="https://github.com/marketplace/actions/quote-readme">
<!--STARTS_HERE_QUOTE_README-->
• <i>“Real artists ship.” — Steve Jobs</i>
<!--ENDS_HERE_QUOTE_README-->
</a>

---

### <img align='center' src='https://media2.giphy.com/media/UQDSBzfyiBKvgFcSTw/giphy.gif' width='29' /> Here’s some humor for you:
<img src="https://readme-jokes.vercel.app/api" alt="Refresh for a new joke" width="11000" />
`;

console.log(readme);
