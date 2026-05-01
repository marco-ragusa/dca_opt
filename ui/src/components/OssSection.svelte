<div class="oss-section">
  <div class="oss-inner">
    <div>
      <div class="oss-kicker">Open source</div>
      <h2 class="oss-headline">A financial tool must be auditable.<br>So the algorithm is public.</h2>
      <p class="oss-text">DCA OPT is MIT licensed, self-hostable in two commands, and built on a straightforward stack: FastAPI backend, Svelte frontend, Yahoo Finance for market data. Your portfolio inputs never leave your machine.</p>
      <p class="oss-text">This project does one thing well. Contributions that significantly expand the scope will be discussed before implementation.</p>
      <div class="oss-links">
        <a class="oss-link" href="https://github.com/marco-ragusa/dca_opt" target="_blank" rel="noopener noreferrer">Star on GitHub</a>
        <a class="oss-link" href="https://github.com/marco-ragusa/dca_opt/blob/master/app/rebalance/rebalance.py" target="_blank" rel="noopener noreferrer">Read the algorithm</a>
        <!--<a class="oss-link" href="https://github.com/marco-ragusa/dca_opt/blob/master/CONTRIBUTING.md" target="_blank" rel="noopener noreferrer">Contributing guide</a>-->
      </div>
    </div>
    <div>
      <div class="quickstart">
        <div class="qs-header">Quick start</div>
        <div class="qs-body">
          <span class="qs-comment"># backend</span>
          <span class="qs-line"><span class="qs-prompt">$</span><span class="qs-cmd">git clone https://github.com/marco-ragusa/dca_opt</span></span>
          <span class="qs-line"><span class="qs-prompt">$</span><span class="qs-cmd">cd dca_opt &amp;&amp; cp .env.example .env</span></span>
          <span class="qs-line"><span class="qs-prompt">$</span><span class="qs-cmd">pip install -r requirements.txt</span></span>
          <span class="qs-line"><span class="qs-prompt">$</span><span class="qs-cmd">uvicorn app.main:app --reload</span></span>
          <br>
          <span class="qs-comment"># frontend</span>
          <span class="qs-line"><span class="qs-prompt">$</span><span class="qs-cmd">cd ui &amp;&amp; npm install</span></span>
          <span class="qs-line"><span class="qs-prompt">$</span><span class="qs-cmd">npm run dev</span></span>
        </div>
      </div>
    </div>
  </div>
</div>
