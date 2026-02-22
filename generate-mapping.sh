#!/usr/bin/env bash
# Generate skill-mapping.tsv: old_path<TAB>new_category
# Uses description.md + directory listing to classify each skill
set -euo pipefail

BASE="/home/project/openclaw/curated_skills"
DESC="$BASE/description.md"
OUT="$BASE/skill-mapping.tsv"

# Header
echo -e "# old_path\tnew_category" > "$OUT"

# Process every skill directory (depth=2, exclude .git)
find "$BASE" -maxdepth 2 -mindepth 2 -type d ! -path '*/.git/*' | sed "s|^${BASE}/||" | sort | while IFS= read -r skill_path; do
  old_cat="${skill_path%%/*}"
  skill_name="${skill_path##*/}"
  
  # Skip trustskill (security scanner, special)
  if [[ "$old_cat" == "trustskill" ]]; then
    echo -e "${skill_path}\tsecurity-compliance" >> "$OUT"
    continue
  fi
  
  # Get description from description.md if available
  desc_line=$(grep "^${skill_path}/SKILL.md:description:" "$DESC" 2>/dev/null || echo "")
  desc_lower=$(echo "$desc_line" | tr '[:upper:]' '[:lower:]')
  
  # Classification logic - order matters, most specific first
  new_cat=""
  
  # ===== SECURITY & COMPLIANCE =====
  if echo "$desc_lower" | grep -qiE 'security scan|vulnerabilit|prompt injection|guardrail|malicious pattern|threat|virus|allowlist|security gate|security hard|zero.trust|mfa|secret word|content moderat'; then
    new_cat="security-compliance"
  
  # ===== SMART HOME & IoT =====
  elif [[ "$old_cat" == "smart-home-iot" ]] || [[ "$old_cat" == "hardware-iot" ]]; then
    if echo "$desc_lower" | grep -qiE 'flight|train|rail|bus|travel|trip|journey|route'; then
      new_cat="travel-transport"
    else
      new_cat="smart-home-iot"
    fi
  
  # ===== GAMES & ENTERTAINMENT =====
  elif echo "$desc_lower" | grep -qiE 'game|chess|battle arena|tamagotchi|digital pet|text adventure|修仙|冒险游戏|剧本杀|spotify|play.?back|apple music|sonos|wiim|winamp|chromecast|media play|roast|clawclash|scrapyard|moltmon|werewolf|hitchhiker|compete.*arena|entertainment'; then
    if echo "$desc_lower" | grep -qiE 'video game|text adventure|chess|battle|arena|修仙|冒险|剧本杀|tamagotchi|digital pet|moltmon|werewolf|hitchhiker|roast|clawclash|scrapyard|compete'; then
      new_cat="games-entertainment"
    elif echo "$desc_lower" | grep -qiE 'spotify|apple music|sonos|wiim|winamp|playback|chromecast|media play'; then
      new_cat="games-entertainment"
    fi
  fi
  
  # ===== TRAVEL & TRANSPORT =====
  if [[ -z "$new_cat" ]]; then
    if echo "$desc_lower" | grep -qiE 'flight|train schedule|rail|bus book|travel plan|trip plan|journey|itinerar|airport|airbnb|hotel|skåne.*transport|google flights|skiplagged|ns api|dutch train|israel rail|futa express|camino.*journey|property.*search|property.*listing|realestate|navifare'; then
      new_cat="travel-transport"
    fi
  fi
  
  # ===== FINANCE & MARKETS =====
  if [[ -z "$new_cat" ]]; then
    if echo "$desc_lower" | grep -qiE 'stock price|stock market|j.quants|edinet|financial statement|investment|金融|決算|有価証券|財務|securities|accounting|bookkeep|pocketsmith|gold price|revenue.?cat|ceo.*performance|s.p 500|八字|六爻|fortune|算命'; then
      new_cat="finance-markets"
    fi
  fi
  
  # ===== AGENT CORE =====
  if [[ -z "$new_cat" ]]; then
    if echo "$desc_lower" | grep -qiE 'task.*(track|state|manage)|memory.*(tier|manage|system|complete|maintenance)|context.*(anchor|compact|recover)|self.improv|session.state|checkpoint|verification checkpoint|clawlist|ibt|deterministic|hello.*(agent|world)|dgr|decision artifact'; then
      new_cat="agent-core"
    fi
  fi
  
  # ===== AGENT ORCHESTRATION =====
  if [[ -z "$new_cat" ]]; then
    if echo "$desc_lower" | grep -qiE 'delegat|model.*(rout|select)|multi.agent|agent.*(orchestrat|spawn|supervis|coordinat)|a2a|bedrock.*agentcore|autonomous.*execution|brainstorm.*refine|kindroid|llm.supervis|manipulation.detect|smart.spawn|context.aware.delegat|kalibr|kimi.*delegat|lygo'; then
      new_cat="agent-orchestration"
    fi
  fi
  
  # ===== SEARCH WEB =====
  if [[ -z "$new_cat" ]]; then
    if echo "$desc_lower" | grep -qiE 'web search|search.*web|duckduckgo|searxng|tavily|exa.*search|brave.*search|google.*search.*tool|metasearch|deepwiki|flaresolverr|cloudflare.*bypass|harpa.*ai|parallel.*search|pcap.*analy|serper|snaprender|screenshot.*url|readeck'; then
      new_cat="search-web"
    fi
  fi
  
  # ===== BROWSER AUTOMATION =====
  if [[ -z "$new_cat" ]]; then
    if [[ "$old_cat" == "browser-automation" ]] || echo "$desc_lower" | grep -qiE 'browser.*automat|playwright|stagehand|headless.*browser|web.*form.*auto|fill.*form|web.*scrape.*automat|browser.*cli|puppeteer|autofillin|blankfiles|riddle|tinyfish|browser-use'; then
      new_cat="browser-automation"
    fi
  fi
  
  # ===== COMMUNICATION & MESSAGING =====
  if [[ -z "$new_cat" ]]; then
    if echo "$desc_lower" | grep -qiE 'email|gmail|smtp|imap|whatsapp|telegram|discord|signal|slack|irc|mqtt|sms|send.*message|chat|feishu|lark|wechat|kakaotalk|zulip|localsend|olvid|notification.*push|outlook|protonmail|mailchannel|himalaya|remindme|pocketalert'; then
      new_cat="communication-messaging"
    fi
  fi
  
  # ===== MEDIA GENERATION =====
  if [[ -z "$new_cat" ]]; then
    if echo "$desc_lower" | grep -qiE 'text.to.speech|tts|voice.*clon|image.*generat|video.*generat|generate.*image|generate.*video|generate.*speech|generate.*audio|generate.*music|ai.*image|midjourney|stable diffusion|flux|veo|dall|suno|music.*generat|song.*generat|podcast.*generat|avatar.*video|lip.sync|nano.banana|gemini.*image|grok.*image|image.*router|vydra|fal\.ai|comfyui|deepdub|clonev|livekit|lunara|yollomi|renderful|masonry.*generat|seedance|seeddance|inworld.*tts|eachlabs.*music'; then
      new_cat="media-generation"
    fi
  fi
  
  # ===== MEDIA PROCESSING =====
  if [[ -z "$new_cat" ]]; then
    if echo "$desc_lower" | grep -qiE 'transcri|speech.to.text|stt|whisper|ocr|ffmpeg|video.*process|audio.*process|document.*convert|pdf.*convert|pandoc|qr.*code|resize.*image|imagemagick|docling|subtitle|caption|extract.*text|voice.*recogni|overleaf|latex|notebooklm|youtube.*summar|youtube.*transcript|video.*download|bilibili.*download|instagram.*download|reel.*download|convert.*document|zerox|pptx|font.*fix|inkjet|print|thermal'; then
      new_cat="media-processing"
    fi
  fi
  
  # ===== CONTENT & PUBLISHING =====
  if [[ -z "$new_cat" ]]; then
    if echo "$desc_lower" | grep -qiE 'twitter|tweet|x.post|linkedin.*post|instagram.*post|blog.*writ|seo|content.*market|social.*media.*post|moltbook|publish.*markdown|resume.*build|ppt.*generat|presentation|slides|viral|copywriting|content.*creation|tiktok.*post|xiaohongshu|wechat.*publish|youtube.*short|nonopost|coconala|fiverr|upwork|product.*image.*generat|klawdin|korean.claw|botmadang|agent.voice|clawdbites|giphy|instaclaw|postfast|hotmention|instagram.*poster|x.timeline|x.trends|xbio|xai.search|chirp|opentweet|content.social|solobuddy|job.description|email.*marketing|cold.*email|prompt.seller|resume.*optim|landing.*page.*roast|content.*engine|slidespeak'; then
      new_cat="content-publishing"
    fi
  fi
  
  # ===== DATA & ANALYTICS =====
  if [[ -z "$new_cat" ]]; then
    if echo "$desc_lower" | grep -qiE 'csv|excel|dashboard|analytics|data.*viz|chart|report.*generat|revenue.*track|saas.*revenue|pipeline.*analyt|kpi|qlik|wakapi|time.*track|data.*structure|data.*reconcil|cochesnet|dnfm|expense.*track.*csv'; then
      new_cat="data-analytics"
    fi
  fi
  
  # ===== KNOWLEDGE & RESEARCH =====
  if [[ -z "$new_cat" ]]; then
    if echo "$desc_lower" | grep -qiE 'research|arxiv|pubmed|knowledge.*graph|rag|semantic.*search|deep.*research|deep.*think|news.*aggregat|news.*fetch|news.*summar|rss|encyclopedia|baidu.*baike|wikipedia|academic.*paper|paper.*review|zotero|corpus|linguist|birdnet|weather.*data|location.*context|ceorater|tnbc|literature|specification.*extract|competitor.*monitor|moltext'; then
      new_cat="knowledge-research"
    fi
  fi
  
  # ===== PRODUCTIVITY & PERSONAL =====
  if [[ -z "$new_cat" ]]; then
    if echo "$desc_lower" | grep -qiE 'task.*manag|todo|pomodoro|calendar|reminder|note.taking|journal|health.*track|fitness|calorie|water.*track|meditation|adhd|focus.*mode|shopping.*list|vocabulary|habit|birthday|personal.*finance|expense.*track|intermittent.*fast|gamification|timer|alarm|hydration|meal.*track|workout|strava|planka|kanban|todoist|timecamp|anki|flashcard|apple.*reminder|apple.*note|craft.*note|notion.*clip|writing.*plan|icloud.*calendar|carddav|meet.*schedul|video.*conference|daily.*plan|idea.*capture|relationship|love|personal.*note|personal.*travel|sleep|samsung.*health|rescuetime|freedcamp'; then
      new_cat="productivity-personal"
    fi
  fi
  
  # ===== BUSINESS OPERATIONS =====
  if [[ -z "$new_cat" ]]; then
    if echo "$desc_lower" | grep -qiE 'crm|salesforce|shopify|woocommerce|saas.*build|saas.*orchestrat|e.commerce|invoic|customer.*relationship|product.*market|goHighLevel|ghl|apollo.*api|outbound.*campaign|coconala.*sell|lead.*enrich|lead.*generat|property.*search|business.*account|due.*diligen|m.a.*analy|营收|dropshipping|abm|product.*research|clawmart|shopclawmart|productboard|talkspresso|pamela.*call|ned.*analytics'; then
      new_cat="business-operations"
    fi
  fi
  
  # ===== DEVOPS & CLOUD =====
  if [[ -z "$new_cat" ]]; then
    if echo "$desc_lower" | grep -qiE 'docker|kubernetes|k8s|velero|cert.manager|railway.*deploy|aws|lightsail|ec2|ci.cd|pipeline.*status|server.*monitor|ssh|dns|godaddy|deploy|cloudstack|launchd|system.*updat|cron.*retry|openclaw.*updat|git.crypt|backup|proxymock|n8n|sandbox|lybic|astra.*docker|bun.*runtime|omarchy|sys.*updater|workspace.*governance'; then
      new_cat="devops-cloud"
    fi
  fi
  
  # ===== DEVELOPER TOOLS =====
  if [[ -z "$new_cat" ]]; then
    if echo "$desc_lower" | grep -qiE 'git.*push|git.*commit|git.*workflow|pr.*review|code.*review|code.*security|lint|ui.ux|tmux|cursor.*cli|opencode|claude.*code|claude.*usage|coding|refactor|scaffold|foundry.*forge|vhs.*record|schema.*markup|technical.*seo|go.*vulnerab|skill.*doctor.*ci|evolve|react.*native|godot|fivem|raycast|shadcn|motion.*dev|swift|symbolpicker|axe.*devtools|accessibility|android.*adb|ios.*view|apple.*hig|hidpi.*mouse|guicountrol|computer.*vision|3d.*visual|pangolin|record.*audio.*screen|install.*scientify'; then
      new_cat="developer-tools"
    fi
  fi

  # ===== INTEGRATIONS & CONNECTORS =====
  if [[ -z "$new_cat" ]]; then
    if echo "$desc_lower" | grep -qiE 'clawhub|clawdhub|skill.*install|google.*workspace|microsoft.*365|m365|airtable|composio|autotask|mcp.*server|devtopia|mcporter|basecamp|gog.*cli|google.*cli|test.*skill|debug|mistakenly|compatibility.*stub|stub'; then
      new_cat="integrations-connectors"
    fi
  fi
  
  # ===== FALLBACK: classify by old category =====
  if [[ -z "$new_cat" ]]; then
    case "$old_cat" in
      agent-infrastructure) new_cat="agent-core" ;;
      ai-agent-orchestration) new_cat="agent-orchestration" ;;
      ai-media-generation) new_cat="media-generation" ;;
      automation) new_cat="productivity-personal" ;;
      browser-automation) new_cat="browser-automation" ;;
      business-data-integration) new_cat="business-operations" ;;
      business-integration) new_cat="business-operations" ;;
      cloud-network) new_cat="devops-cloud" ;;
      communication) new_cat="communication-messaging" ;;
      communication-email) new_cat="communication-messaging" ;;
      content-media) new_cat="content-publishing" ;;
      content-social) new_cat="content-publishing" ;;
      data-analytics) new_cat="data-analytics" ;;
      data-integration) new_cat="integrations-connectors" ;;
      developer-tools) new_cat="developer-tools" ;;
      development-system-tools) new_cat="developer-tools" ;;
      development-workflows) new_cat="developer-tools" ;;
      devops-infrastructure) new_cat="devops-cloud" ;;
      finance-data-services) new_cat="finance-markets" ;;
      hardware-iot) new_cat="smart-home-iot" ;;
      information-research) new_cat="knowledge-research" ;;
      integrations-apis) new_cat="integrations-connectors" ;;
      knowledge-research) new_cat="knowledge-research" ;;
      media-content) new_cat="media-processing" ;;
      media_content) new_cat="media-processing" ;;
      media-entertainment) new_cat="games-entertainment" ;;
      media-processing) new_cat="media-processing" ;;
      mobile-design) new_cat="developer-tools" ;;
      productivity) new_cat="productivity-personal" ;;
      productivity-automation) new_cat="productivity-personal" ;;
      productivity-task-management) new_cat="productivity-personal" ;;
      productivity-tools) new_cat="productivity-personal" ;;
      smart-home-iot) new_cat="smart-home-iot" ;;
      system-developer-tools) new_cat="developer-tools" ;;
      trustskill) new_cat="security-compliance" ;;
      utilities) new_cat="productivity-personal" ;;
      web-communication-tools) new_cat="integrations-connectors" ;;
      web-search) new_cat="search-web" ;;
      web-services) new_cat="integrations-connectors" ;;
      *) new_cat="integrations-connectors" ;;  # catch-all
    esac
  fi
  
  echo -e "${skill_path}\t${new_cat}" >> "$OUT"
done

echo "Generated mapping: $(grep -c $'\t' "$OUT") entries in $OUT"
