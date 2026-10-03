# -*- coding: utf-8 -*-
"""Generate the notes / journal index + detail pages for the site."""
import os
import html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")

NAV = [
    ("home", "../index.html", "最初一页", None),
    ("profile", "../profile/index.html", "关于我", None),
    ("projects", "../projects/index.html", "做过的事", "(案例)"),
    ("notes", "../notes/index.html", "写下的字", None),
    ("journal", "../journal/index.html", "日常与照片", None),
]


def header(page, title, desc):
    items = []
    for key, href, label, sub in NAV:
        href = "index.html" if key == page else href
        sub_html = "<span>%s</span>" % sub if sub else ""
        items.append('<li><a href="%s" data-nav="%s">%s</a>%s</li>' % (href, key, label, sub_html))
    nav = "\n          ".join(items)
    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, minimum-scale=1.0, maximum-scale=1.0, user-scalable=no">
<meta name="format-detection" content="telephone=no">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="icon" href="../img/favicon.svg" type="image/svg+xml">
<link media="screen" href="../css/style.css" type="text/css" rel="stylesheet">
</head>
<body data-page="{page}">
<div id="wrapper">

  <header>
    <h1 class="id"><a href="../index.html">SONGLIN</a></h1>
    <div class="todays_date"></div>

    <nav>
      <div id="globalnav">
        <ul>
          {nav}
          <li>
            <ul class="snsnav">
              <li><a href="mailto:hello@example.com" title="邮箱 Email">ML</a></li>
              <li><a href="https://www.linkedin.com/" target="_blank" rel="noopener" title="领英 LinkedIn">LI</a></li>
              <li><a href="https://github.com/" target="_blank" rel="noopener" title="GitHub">GH</a></li>
              <li><a href="#" title="微信 WeChat">WX</a></li>
            </ul>
          </li>
        </ul>
      </div>
    </nav>

    <div class="name_ja">
      <div class="name_1">王</div>
      <div class="name_2"><span>松</span></div>
      <div class="name_3"><span>林</span></div>
    </div>

    <div class="name_en">
      <div class="top"><span>S</span><span>O</span><span>N</span><span>G</span></div>
      <div class="btm"><span>L</span><span>I</span><span>N</span></div>
    </div>
  </header>

  <div id="container">
    <main>
      <div id="main_contents" class="hm">
""".format(title=html.escape(title), desc=html.escape(desc), page=page, nav=nav)


TRIP = """
      <div class="trip" id="random-trip"
           data-trips='[
             {"url":"../journal/index.html","image":"../img/trip-01.jpg","title":"从工单到现场：一次跨时区的协作","place":"SYDNEY"},
             {"url":"../journal/index.html","image":"../img/trip-02.jpg","title":"把排查清单写成了一首诗","place":"MELBOURNE"},
             {"url":"../journal/index.html","image":"../img/trip-03.jpg","title":"深夜值班时的一盏灯","place":"BRISBANE"}
           ]'>
        <div class="img">
          <img src="../img/trip-01.jpg" alt="照片">
        </div>
        <div class="text_area">
          <a href="../journal/index.html">
            <h2 class="title">从工单到现场：一次跨时区的协作</h2>
            <div class="place">SYDNEY</div>
          </a>
          <div class="from">From My Journal</div>
        </div>
      </div>
"""

FOOT = """      </div>

{other}
    </main>
  </div>

  <footer>
    <div id="copyright"><small>COPYRIGHT &copy; WANG SONGLIN. ALL RIGHTS RESERVED.</small></div>
  </footer>

</div>
<script src="../js/main.js"></script>
</body>
</html>
"""


# ---------------------------------------------------------------- content ---
NOTES = [
    dict(
        slug="last-mile",
        date="2026.09.20", cat="AI 交付", img="note-01.jpg",
        title="从「能用」到「愿意用」：AI 落地的最后一公里",
        excerpt="技术跑通只是起点。真正难的是让客户愿意持续用下去——这三年做宽带排障，我大概就是在练这件事。",
        lead="很多人以为 AI 交付的难点在模型选型和技术集成。做了三年宽带排障之后，我的看法正好相反：技术那一公里，厂商和工程师会替你走完；剩下那一公里，得有人站在客户身边。",
        body="""
<p>先说一件小事。我们的自助排查流程上线第一个月，拦截率只有 12%，远低于预期。团队的第一反应是「流程做得不好」，准备推倒重来。我去翻了那些被转人工的工单，发现一个很朴素的规律：客户卡住的地方，几乎都不是技术问题，而是<strong>不知道自己在看什么</strong>。</p>

<p>页面上写着「请检查光猫指示灯是否正常」。可什么叫「正常」？灯是绿的但闪得快算不算？客户不知道，于是放弃。我们把那句话改成「只要不是红色，就算正常；如果闪得很快，说明正在同步，等两分钟再看」，拦截率就上去了。</p>

<h2>愿意用，是一个关于「确定感」的问题</h2>

<p>技术人习惯用「能不能跑通」衡量一件事，客户用的是另一套标准：<em>我照着做，会不会出错？出错了谁来兜？</em>这两套标准的差距，就是最后一公里。</p>

<p>所以我现在判断一个 AI 交付有没有成，不看调用量，看三件事：</p>

<ul>
  <li>一线同事会不会在没有 KPI 压力的情况下主动打开它；</li>
  <li>出了问题，他们是绕过它，还是回来告诉你哪里不对；</li>
  <li>有没有人开始往里补内容——哪怕只是一句「这个情况我遇到过」。</li>
</ul>

<p>第三条最准。工具被「使用」和工具被「喂养」是两件完全不同的事，后者才是真正的落地。</p>

<h2>把「最后一公里」拆成可执行的动作</h2>

<p>这三年我慢慢摸出一套还算好用的做法，不复杂，但每一条都是踩坑换来的：</p>

<ol>
  <li><strong>先跟一遍真实的活。</strong>不是访谈，是坐在旁边看他怎么操作，包括他切了多少个标签页、在哪一步叹了口气。</li>
  <li><strong>把交付物的语言换成客户的母语。</strong>不是把技术术语翻译成中文，而是翻译成「他下班前会跟同事说的话」。</li>
  <li><strong>留一个随时能退回去的门。</strong>自助流程要能一键转人工，AI 建议要能一键否决。有退路，人才敢往前走。</li>
  <li><strong>把第一批用户变成合作者。</strong>让他们参与定义「什么叫做得好」，而不是等做完了再培训。</li>
</ol>

<blockquote>AI 落地的最后一公里，和宽带排障的最后一公里本质上是同一件事：技术能不能跑通是一回事，客户愿不愿意用、能不能持续用，是另一回事。</blockquote>

<p>我现在把这句话写在自己的工作说明里。它不高级，但它能帮我在每一个岔路口做出判断——当技术方案和客户体验冲突的时候，我知道该往哪边站。</p>
""",
    ),
    dict(
        slug="ai-teammate",
        date="2026.08.11", cat="工具", img="note-02.jpg",
        title="我把 AI 变成了一个排障搭子",
        excerpt="不是让 AI 替我判断，而是让它替我记住。三年工单量堆起来，人的记性是不够用的。",
        lead="我不太喜欢「用 AI 替代人工」这个说法。在我这里，AI 干的是另一件事：它替我记住我记不住的东西，然后在我需要的时候递过来。",
        body="""
<p>排障这件事，难的从来不是单点知识，而是<strong>联想</strong>。客户说「晚上八点以后网就慢」，你得同时想到：是不是小区共享带宽的晚高峰、是不是某个固件版本的已知问题、是不是上个月同一片区报过类似的单。这三条线索分别躺在三个系统里。</p>

<p>人的工作记忆只有那么点大。所以我做的事情很简单：把这三类信息在提问的瞬间一起摆到我面前。</p>

<h2>我的用法：三句话的输入</h2>

<p>我不写复杂的 Prompt，日常就是三句话：</p>

<ul>
  <li>客户原话是什么（尽量保留他的用词，不要翻译）；</li>
  <li>已经做过的动作和结果；</li>
  <li>我需要你帮我想什么（列可能性 / 找相似工单 / 生成给客户的解释）。</li>
</ul>

<p>第三条最关键。同一个现象，「帮我列出可能原因」和「帮我写一段能直接发给客户的话」，得到的东西完全不一样。</p>

<h2>它做不好的事，我也说清楚</h2>

<p>有一段时间我差点被它带偏。它会非常自信地给出一个听起来很合理、但实际不成立的判断——因为历史工单里正好有一条相似的。相似不等于相同，而 AI 对「相似」的把握比人松得多。</p>

<p>所以我给自己立了一条规矩：<strong>AI 负责提可能性，人负责做决定，而且这个决定要能被追溯</strong>。每次采纳它的建议，我都会在工单备注里写一句「依据是什么」。这既是对客户负责，也是我后来能整理出两百多条知识库条目的原因。</p>

<h2>一年下来的变化</h2>

<p>最直接的变化是同类工单的处理时长短了约三成。但我觉得更有价值的，是它改变了我的注意力分配——以前我把大量精力花在「想起来」，现在花在「判断」和「沟通」上。而后面这两件事，恰好是短时间内 AI 还替不了的。</p>
""",
    ),
    dict(
        slug="prompt-for-non-tech",
        date="2026.07.05", cat="方法论", img="note-01.jpg",
        title="给非技术同事讲 Prompt：我常用的三个套路",
        excerpt="不讲框架，不讲角色扮演。只讲三个他们第二天就能用上的动作。",
        lead="同事问我「怎么用 AI」，如果我回一句「你要学会写好 Prompt」，对话就结束了。所以后来我只讲三个动作，每个都能在十分钟内学会。",
        body="""
<h2>套路一：把「我要什么」换成「我要什么形状的东西」</h2>

<p>大部分人第一次用 AI，说的是「帮我看看这个工单」。结果得到一段泛泛而谈的话。问题不在 AI，在于没说清楚<strong>交付物的形状</strong>。</p>

<p>我会让他们补一句：「用三段话，第一段给客户看，第二段给我看，第三段是给上级的升级理由。」形状一确定，内容立刻就具体了。</p>

<h2>套路二：先给一个坏例子</h2>

<p>这招是从带新人里学来的。你跟人解释「什么叫好的排查清单」，不如直接给两份对比：一份是「检查设备状态」，一份是「看光猫的 LOS 灯，红灯说明光纤断了，直接派单」。</p>

<p>对 AI 也一样。我会附一句「不要写成前一种」。<em>告诉它什么不行，比告诉它什么行更有效</em>——因为「行」的标准往往是隐性的，而「不行」是显性的。</p>

<h2>套路三：让它反问你</h2>

<p>这是我最推荐的一招，也是最反直觉的。在提问的最后加一句：「在回答之前，先问我三个你需要知道的问题。」</p>

<p>大部分时候，它问出来的三个问题，正好就是我自己没想清楚的地方。这个动作不产出答案，但它省下了最贵的东西：方向性的返工。</p>

<h2>不要教框架</h2>

<p>我试过给大家讲结构化 Prompt 的模板，效果很差——记住模板的人很少，用得上的人更少。后来我改成「三个动作」，反而传开了。</p>

<p>原因大概是：<strong>框架解决的是完备性问题，而普通人需要的是启动问题</strong>。先让他动起来，剩下的他会自己在用的过程里补齐。</p>
""",
    ),
    dict(
        slug="checklist-not-manual",
        date="2026.06.14", cat="方法论", img="note-03.jpg",
        title="为什么我不再写「排查手册」，改写成「检查清单」",
        excerpt="手册是给人读的，清单是给人用的。这个区别，决定了一份文档会不会真的被打开。",
        lead="我写过一本很漂亮的手册，四十七页，排版认真，还做了目录。上线三个月，打开率个位数。后来我把它拆成了清单，反而被用起来了。",
        body="""
<p>手册和清单的区别，不在长度，在<strong>使用时机</strong>。</p>

<p>手册是「没事的时候读的」——你想学习、想系统了解。清单是「有事的时候翻的」——你正在跟客户通话，需要立刻知道下一步做什么。这两种场景对人的要求完全不同：前者需要结构，后者需要速度。</p>

<h2>清单的三条规矩</h2>

<ol>
  <li><strong>一步一个动作。</strong>「检查线路质量」不是动作，「看路由器 WAN 口灯是否常亮」才是。</li>
  <li><strong>每一步都要能判断成败。</strong>没有判断标准的步骤，等于把问题又推回给了一线。</li>
  <li><strong>按概率排序，不按逻辑排序。</strong>手册按「从物理层到应用层」排，清单按「先查最常见的原因」排。</li>
</ol>

<p>第三条是最大的改变。以前我总想把知识组织得「正确」，现在我只想让它<strong>管用</strong>。80% 的同类问题由前三个步骤解决，那这三个步骤就该在最上面，哪怕它们在教科书里排在后面。</p>

<h2>顺带解决了一个老问题</h2>

<p>清单化之后，新人上手快了很多。原因不是清单写得清楚，而是<strong>清单可以被打勾</strong>。一个可以打勾的流程，天然带着进度感和完成感；而一本手册，你永远不知道自己读到哪了。</p>

<p>现在回头看，那本四十七页的手册并没有白写——它是我的思考过程。只是我把思考留给自己，把清单交给别人。</p>
""",
    ),
    dict(
        slug="certainty",
        date="2026.05.02", cat="客户体验", img="note-04.jpg",
        title="客户要的不是答案，是确定感",
        excerpt="一次让我记了很久的对话：我给了正确答案，客户却更生气了。",
        lead="有一次我十分钟定位了故障、给出了准确的处理方案，客户在电话那头却越来越不耐烦。挂了电话我想了很久，才明白问题出在哪。",
        body="""
<p>那次的情况不复杂：光猫的老化导致间歇性丢包。我很快确认了原因，告诉客户「设备老化，我们安排更换」。我以为这是个好结局——问题解决了，方案也明确。</p>

<p>但客户的反应是：「所以你们早就知道这个设备有问题？」</p>

<p>他关心的不是「能不能修好」，而是「为什么是我遇到」「要等多久」「中间还会不会断」。我给的是一份技术结论，他要的是一份<strong>关于接下来会发生什么的说明书</strong>。</p>

<h2>把「答案」翻译成「确定感」</h2>

<p>后来我养成了一个习惯，处理完任何工单，都用三句话收尾：</p>

<ul>
  <li><strong>发生了什么：</strong>用一句话说清原因，不堆术语。</li>
  <li><strong>接下来会发生什么：</strong>谁联系你、什么时候、要你配合做什么。</li>
  <li><strong>如果又出问题：</strong>找谁、怎么找、大概多久能响应。</li>
</ul>

<p>这三句话不增加任何技术含量，但它们把客户从「被动等待」变成了「知道进程」。催单率下降的很大一部分，我觉得来自这里。</p>

<h2>这件事和 AI 交付的关系</h2>

<p>后来我做 AI 工具的落地，发现是同一回事。用户第一次面对一个新工具时的心理，和客户面对一个陌生故障时一模一样：<em>我不知道它会怎么对我。</em></p>

<p>所以上线一个新功能，我现在一定会附上一段「如果你不放心，可以这样退回去」。这段说明看起来是在降低期待，实际上是在提高采纳率。</p>
""",
    ),
    dict(
        slug="tidy-notes",
        date="2026.03.28", cat="工具", img="note-02.jpg",
        title="我如何用 AI 整理三年的排障笔记",
        excerpt="从一千多条零散记录到两百多条结构化条目，我踩过的三个坑。",
        lead="三年下来，我的工单备注加起来一千多条。它们是我的经验，也是一座没人愿意爬的垃圾山。我想把它变成能用的东西，试了三次才找到办法。",
        body="""
<h2>坑一：想让 AI 一次整理完</h2>

<p>第一次我把几百条备注一起丢进去，要求它归类、提炼、生成知识库。结果是它非常努力地编造了一些看起来很像那么回事、但实际上我没遇到过的案例。规模一大，它就开始「补全」。</p>

<p>后来我改成<strong>一次二十条</strong>，并且明确要求「只允许使用我给的内容，不确定的标出来」。产出变慢，但可信度上来了。</p>

<h2>坑二：没有统一的模板</h2>

<p>第二次我让它自由发挥，结果每条格式都不一样：有的写现象，有的写原因，有的写处置。它们单独看都不错，合在一起就没法检索。</p>

<p>所以我先定死模板——<strong>现象 / 可能原因 / 验证方法 / 处置动作</strong>——再让它按模板填。模板是我定的，这一点很重要：把结构交给 AI 决定，等于把分类权交出去。</p>

<h2>坑三：整理完就结束了</h2>

<p>整理出来的两百多条，前两个月确实好用。然后开始过期——固件升级了、流程改了、设备换代了。没有维护机制的知识库，衰变速度比我想象的快得多。</p>

<p>现在的做法很轻：<strong>每结一个复杂工单，就补一条或改一条</strong>。不设 KPI，不搞定期大扫除，就靠这个动作让库保持活着。</p>

<h2>回到出发点</h2>

<p>回头看，这件事里 AI 帮我省掉的是体力活——分类、改写、查重。真正决定成败的三件事，都是我做的：<strong>定模板、控规模、建机制</strong>。</p>

<p>我越来越觉得，用好 AI 的关键不在于会不会提问，而在于你有没有想清楚「这件事的结构长什么样」。想清楚了，AI 就是个放大器；没想清楚，它只会把混乱放大。</p>
""",
    ),
    dict(
        slug="career-switch",
        date="2026.02.16", cat="职业", img="note-01.jpg",
        title="转岗笔记：从售后支持到 AI 交付，我补的三门课",
        excerpt="不是学 Python。我给自己排的三门课，一门比一门不像技术课。",
        lead="决定转向 AI 交付之后，我列过一张学习清单，上面写着 Python、机器学习、大模型原理。学了两周我发现，这张清单有问题。",
        body="""
<p>问题在于：我把自己当成了一个要从零开始的技术人。但我真正带得走的资产，不是编码能力，是三年里积累的<strong>另一种能力</strong>——把技术翻译成人能听懂的话，把混乱的现场梳理成可执行的步骤。</p>

<p>所以我把清单重排了，变成三门课。</p>

<h2>第一门：把 Prompt 当成交付物来设计</h2>

<p>不是「学会写 Prompt」，而是把它当成一个要被别人使用的产品。它有没有边界条件？出错的时候表现是什么样？一个没写过 Prompt 的同事，能不能照着改？</p>

<p>我开始用写交付文档的标准来写 Prompt：明确输入、明确输出、明确不做什么。这件事我上手很快，因为它和我写排查清单的方法完全一样。</p>

<h2>第二门：理解 AI 的「失败方式」</h2>

<p>不需要懂反向传播，但必须知道它<strong>会怎么错</strong>。它会自信地编造、会被相似案例带偏、会在规模变大时悄悄「补全」。知道这些，我才能在设计流程时预留退路。</p>

<p>这门课我学得最认真，因为它直接决定了我能不能对客户说「放心用」。</p>

<h2>第三门：把人放回流程图里</h2>

<p>这门课没有教材。它的内容是：当 AI 给的建议和一线同事的经验冲突时，怎么办？当工具让某个人觉得自己被替代时，怎么办？</p>

<p>我的答案是：<strong>永远把人的判断留在最后一环</strong>，并且在流程里明确写出来。这既是尊重，也是容错设计。</p>

<h2>现在的状态</h2>

<p>我不觉得自己在「转行」，更像是把同一件事换了个赛道做：以前让客户愿意继续用宽带，现在让客户愿意继续用 AI。两者的最后一公里，是同一条路。</p>
""",
    ),
    dict(
        slug="three-things",
        date="2026.01.09", cat="随笔", img="note-03.jpg",
        title="关于「最后一公里」的三点体会",
        excerpt="写给一年后的自己。如果那时候我还在做交付，希望这三条还成立。",
        lead="新的一年开始，给自己留三条笔记。不宏大，但都是摔过跟头之后才写下来的。",
        body="""
<h2>一、交付不是终点，是起点</h2>

<p>我见过太多「成功上线」的项目，三个月后没人打开。上线那天所有人都在庆祝，但真正的考验在那之后——当新鲜感退去、当第一个人遇到麻烦、当有人开始说「还不如以前那样」。</p>

<p>所以我现在会把上线日当成第一天，而不是最后一天。这意味着在项目计划里，上线之后的陪伴期必须占足够的分量。这一条我吃过亏。</p>

<h2>二、让人做决定，让工具做准备</h2>

<p>这是我做 AI 工具最核心的一条原则。工具负责把所有相关信息在需要的那一刻摆到人面前，但最后的判断必须由人做出，并且这个人要能为结果负责。</p>

<p>反过来做——让工具做决定、让人执行——短期效率可能更高，但一旦出错，整个链条会失去信任。而信任一旦没了，再好的工具都推不动。</p>

<h2>三、把「被使用」当成唯一的验收标准</h2>

<p>不是功能清单打勾，不是测试通过率，也不是上线仪式。是三个月后，还有多少人在没有要求的情况下主动打开它。</p>

<p>这个标准很残酷，因为它把所有「其实没人用」的项目都暴露出来了。但我觉得这是唯一诚实的标准。</p>

<blockquote>技术能不能跑通是一回事，客户愿不愿意用、能不能持续用，是另一回事。而我擅长的，恰恰是后面这件事。</blockquote>

<p>一年后回来看，希望这三条还成立。</p>
""",
    ),
]

JOURNAL = [
    dict(
        slug="2026-0928",
        date="( Sep. 28th, 2026 )", img="journal-01.jpg",
        title="夜班之后的那个清晨",
        excerpt="值完夜班回家，路上把三种高频工单的清单改完了最后一遍。太阳升起来的时候我在想，这件事为什么让我这么兴奋。",
        body="""
<p>夜班结束是早上六点二十。天刚亮，路上没什么人。我没有直接回家，在便利店买了咖啡，坐在门口的台阶上把清单的最后一段改完。</p>

<p>改的是「网速异常」那一类。原来的第一步是「确认带宽套餐」，我把它挪到了第三步，把「确认是否在晚高峰时段」提到了最前面。原因很简单：我值了这么多夜班，发现大部分「网速慢」的投诉其实发生在晚上八点到十一点之间，而套餐本身没任何问题。</p>

<h2>关于兴奋这件事</h2>

<p>我一开始以为自己兴奋是因为效率——清单确实省时间。但坐在台阶上想了一会儿，我发现不是。</p>

<p>真正让我兴奋的是：<strong>我把一件只存在于我脑子里的经验，变成了别人也能用的东西。</strong>以前这类判断只属于老员工的手感，现在它被写下来了，一个新人在第二周就能用上。</p>

<p>这和写代码、做设计不太一样。它的价值不在产物本身，在于它让某个不在场的人少走了一段路。</p>

<figure>
  <img src="../img/journal-01.jpg" alt="清晨的街道">
  <figcaption>六点二十的街道，咖啡和改到一半的清单。</figcaption>
</figure>

<p>回家睡了四个小时。下午起来的时候，看到同事在群里回了一句「这个清单好用」。就这一句，我觉得夜班值了。</p>
""",
    ),
    dict(
        slug="2026-0902",
        date="( Sep. 2nd, 2026 )", img="journal-02.jpg",
        title="一张工单教我的事",
        excerpt="客户坚持说「就是你们的问题」，我查了两小时没找到。最后发现问题出在他家新买的智能音箱上。",
        body="""
<p>这张工单我记了很久，因为它几乎推翻了我当时的判断方式。</p>

<p>客户报的是「每天下午断网两三次」。我查了线路、查了局端日志、查了同片区其他用户，全部正常。客户在电话里很坚定：「就是你们的问题，我什么都没动过。」</p>

<p>两小时后我几乎要放弃了。转折点是我问了一句不在我标准清单上的话：「最近家里有没有添什么新东西？」</p>

<h2>一个智能音箱</h2>

<p>他上个月买了个智能音箱，插在光猫旁边，一直通电。问题出在这里——它的电源适配器质量一般，工作时会产生干扰，恰好影响到了相邻的线路。</p>

<p>拔掉之后，断网消失了。</p>

<h2>我把这句话加进了清单</h2>

<p>「最近家里有没有添置新的电子设备？」现在这是「频繁掉线」类清单的固定一问。</p>

<p>技术上它一点都不高级，甚至有点土。但它提醒了我一件事：<strong>标准流程解决的是标准问题，而真实世界总有一部分不在流程里。</strong>清单要留一行给「清单之外」。</p>

<p>我现在给每份清单的最后一步都写着：「如果以上都不成立，回到最基础的问题——最近有什么变化？」</p>
""",
    ),
    dict(
        slug="2026-0815",
        date="( Aug. 15th, 2026 )", img="journal-03.jpg",
        title="搬家、网线，和第一次远程陪跑",
        excerpt="第一次做远程陪跑，对面是一个刚入职两周的新同事。我在屏幕这头看着他操作，突然理解了什么叫「交付」。",
        body="""
<p>这周搬了家。收拾东西的时候翻出来一捆网线，是我刚入职时买的，那时候觉得「做网络的总得有几根网线吧」。三年过去，一根都没用上。</p>

<p>更有意思的是周五那次远程陪跑。团队来了个新同事，入职两周，第一次独立处理复杂工单。我开着视频在旁边看，不出声。</p>

<h2>看着别人用你做的东西</h2>

<p>前十分钟我很想插嘴。他跳过了清单里的第二步，直接去了一个我知道会绕远路的方向。但按我给自己定的规矩，陪跑时只在被问到的时候说话。</p>

<p>结果他自己绕回来了。他在第四步卡住，回头翻清单，发现了第二步，然后说了一句：「哦，原来要先看这个。」</p>

<p>那一刻比我自己解决问题还有成就感。因为<strong>清单在他手里完成了一次教学</strong>，而我不在场。这正是我想要的交付状态：不是我一直在，而是我不在也行。</p>

<h2>关于搬家的一点感慨</h2>

<p>新家的宽带是我自己装的。装的时候发现，我现在的排查顺序和刚入职时完全不同了——以前从设备开始，现在从「客户会怎么描述这个现象」开始。</p>

<p>大概这就是三年留下的东西。它不是知识，是视角。</p>
""",
    ),
    dict(
        slug="2026-0721",
        date="( Jul. 21st, 2026 )", img="journal-01.jpg",
        title="把清单写成了一首诗",
        excerpt="同事说我写的排查清单「读起来像说明书」。我试着改了改，结果变成了另一种东西。",
        body="""
<p>团队里有人跟我说：「你写的清单太干了，读起来像说明书。」我第一反应是「清单本来就不该好看」，但回家路上一直在想这句话。</p>

<p>第二天我做了个实验。我把「频繁掉线」那份清单重写了一遍，把每一步的判断标准换成了客户会说的话：</p>

<ul>
  <li>灯是红的，还是别的颜色？</li>
  <li>是偶尔闪一下，还是每隔几分钟就断？</li>
  <li>断的时候，是全家都没网，还是只有手机没网？</li>
</ul>

<p>改完之后它读起来确实不像说明书了，倒有点像一份问诊记录。</p>

<h2>意外的好处</h2>

<p>重写之后我发现了一件事：<strong>用客户的语言描述问题，会让排查路径本身变得更清楚。</strong>因为客户的语言天然带着场景，而场景会暴露线索。「全家都没网」和「只有手机没网」是完全不同的两个方向，以前我的清单里没有这个区分。</p>

<p>所以那句「太干了」，其实是在提醒我漏掉了信息。</p>

<h2>写在最后</h2>

<p>我现在写清单有一个习惯：先写技术版本，再改写成客户版本。两份都要写。技术版本给同事看，客户版本给对话用。</p>

<p>它们其实是同一份东西的两种语言。而翻译的过程，往往就是发现漏洞的过程。</p>
""",
    ),
    dict(
        slug="2026-0610",
        date="( Jun. 10th, 2026 )", img="journal-02.jpg",
        title="深夜值班时的一盏灯",
        excerpt="凌晨两点，一个客户的宽带断了。他打来电话的第一句话是「不好意思这么晚」。",
        body="""
<p>凌晨两点十五分，电话进来。客户的第一句话是：「不好意思这么晚打扰你，我明天有个很重要的线上会议。」</p>

<p>这句话让我一下子清醒了。他不是在抱怨，他是在道歉——为了自己的网络坏在一个不方便的时间而道歉。</p>

<h2>十分钟</h2>

<p>问题不难，是光猫的一个已知固件问题，重启之后恢复。前后不到十分钟。挂电话之前他说了三遍谢谢。</p>

<p>值班室的灯很亮，亮到有点刺眼。挂完电话我坐了一会儿，想的是同一件事：<strong>他本来可以明天再打，但他选择了两点打过来，因为那场会议对他很重要。</strong></p>

<p>我们做的事情在技术层面很小，但在他的时间线上占的位置不小。这个认知后来影响了我对「优先级」的判断——我不再只看工单的标签，也开始看客户描述里的时间词。「明天」「这周」「今天之内」，这些词比标签更能说明紧急程度。</p>

<h2>一点私心</h2>

<p>我在那份清单里加了一行注释：「如果客户主动道歉，说明这件事对他很重要，请优先处理。」</p>

<p>同事说这条太感性了，不适合放在清单里。我没有删。我觉得流程里应该留一点这样的东西——它不提高效率，但它提醒我们面对的是人。</p>
""",
    ),
    dict(
        slug="2026-0512",
        date="( May. 12th, 2026 )", img="journal-03.jpg",
        title="第一次被客户说「谢谢，我懂了」",
        excerpt="以前客户说「谢谢」，是客套。这一次他说的是「我懂了」。",
        body="""
<p>这三年来我大概接过上千通电话，听过很多次「谢谢」。大部分时候那是礼貌性的结束语。但这周有一次不一样。</p>

<p>客户是一位六十多岁的阿姨，家里网络时断时续。排查过程没什么特别，问题是路由器放在弱电箱里、信号被金属箱体挡住了。我建议她把路由器挪出来。</p>

<h2>她说「我懂了」</h2>

<p>我解释完，她沉默了两秒，然后说：「哦，就是把它放在铁盒子里，信号出不来是吧？那我懂了。」</p>

<p>那一刻的感觉很难形容。她没有说「好的谢谢」，她说的是「我懂了」。<strong>客套是关系的结束，「我懂了」是关系的开始</strong>——她以后遇到类似问题，自己就能处理，甚至可以告诉邻居。</p>

<h2>我开始在意这个区别</h2>

<p>从那以后，我会有意识地把「解释」换成「让她能复述」。具体做法很简单：说完之后加一句「我这样说清楚吗？您能用自己的话跟我说一遍吗？」</p>

<p>这个动作会多花三十秒。但它换来的是客户从「被动等待救援」变成「有能力自己处理」。对我这种做交付的人来说，这三十秒是我最愿意花的时间。</p>

<figure>
  <img src="../img/journal-03.jpg" alt="窗边的路由器">
  <figcaption>把路由器从弱电箱里挪出来之后，信号强了一格。</figcaption>
</figure>

<p>现在做 AI 工具落地，我的验收标准里也有这么一条：用户能不能用自己的话，把工具能帮他做什么讲给别人听。讲得出来，才算真的落地了。</p>
""",
    ),
]


# ---------------------------------------------------------------- builders ---
def build_notes_index():
    items = []
    for n in NOTES:
        items.append(
            """            <div class="item">
              <a href="{slug}.html">
                <span class="meta">{date} &middot; {cat}</span>
                <span class="title">{title}</span>
                <span class="excerpt">{excerpt}</span>
              </a>
            </div>""".format(
                slug=n["slug"], date=n["date"], cat=n["cat"],
                title=html.escape(n["title"]), excerpt=html.escape(n["excerpt"]),
            )
        )
    body = header("notes", "写下的字 · 王松林",
                  "关于 AI 落地、排障方法论与客户体验的随笔。") + """
        <div class="index_outer notes_index inner">

          <div class="page_intro">
            <div>
              <p class="lead">写下的字，都关于同一件事。</p>
              <p>
                这里是我关于 AI 交付、排障方法论和客户体验的随笔。它们大多写在下班之后，起因往往是一张具体的工单，或者一次没想明白的对话。没有结论，只有过程。
              </p>
            </div>
          </div>

          <div class="list">
%s
          </div>

        </div>
""" % "\n".join(items)
    out = body + FOOT.format(other=TRIP)
    write("notes/index.html", out)


def build_notes_detail():
    for i, n in enumerate(NOTES):
        prev_n = NOTES[i - 1] if i > 0 else None
        next_n = NOTES[i + 1] if i < len(NOTES) - 1 else None
        left = ('<a class="prev" href="%s.html"><span>上一篇</span>%s</a>'
                % (prev_n["slug"], html.escape(prev_n["title"]))
                if prev_n else
                '<a class="prev" href="index.html"><span>返回</span>写下的字</a>')
        right = ('<a class="next" href="%s.html"><span>下一篇</span>%s</a>'
                 % (next_n["slug"], html.escape(next_n["title"]))
                 if next_n else
                 '<a class="next" href="../projects/index.html"><span>继续</span>看看项目案例</a>')
        body = header("notes", "%s · 王松林" % n["title"], n["excerpt"]) + """
        <div class="index_outer inner">
          <article class="article_detail">
            <div class="meta">{date} &middot; {cat}</div>
            <h1 class="detail_head">{title}</h1>
            <p class="detail_lead">{lead}</p>
            <div class="body">{body}</div>
            <div class="detail_foot">
              {left}
              {right}
            </div>
          </article>
        </div>
""".format(
            date=n["date"], cat=n["cat"], title=html.escape(n["title"]),
            lead=html.escape(n["lead"]), body=n["body"].strip(),
            left=left, right=right,
        )
        write("notes/%s.html" % n["slug"], body + FOOT.format(other=TRIP))


def build_journal_index():
    items = []
    for j in JOURNAL:
        items.append(
            """            <div class="item">
              <a href="{slug}.html">
                <div class="text_area">
                  <span class="date">{date}</span>
                  <p class="excerpt">{excerpt}</p>
                </div>
                <div class="img">
                  <img src="../img/{img}" alt="{title}">
                </div>
              </a>
            </div>""".format(
                slug=j["slug"], date=j["date"], img=j["img"],
                excerpt=html.escape(j["excerpt"]), title=html.escape(j["title"]),
            )
        )
    body = header("journal", "日常与照片 · 王松林",
                  "值班日志、生活片段，和一些想明白或没想明白的事。") + """
        <div class="index_outer journal_index inner">

          <div class="page_intro">
            <div>
              <p class="lead">日常与照片。</p>
              <p>
                这里没有方法论，只有日子。值完夜班的清晨、一张让我记很久的工单、搬家时翻出来的一捆网线。写下来是因为它们比结论更接近真实。
              </p>
            </div>
          </div>

          <div class="list">
%s
          </div>

        </div>
""" % "\n".join(items)
    write("journal/index.html", body + FOOT.format(other=TRIP))


def build_journal_detail():
    for i, j in enumerate(JOURNAL):
        prev_j = JOURNAL[i - 1] if i > 0 else None
        next_j = JOURNAL[i + 1] if i < len(JOURNAL) - 1 else None
        left = ('<a class="prev" href="%s.html"><span>上一篇</span>%s</a>'
                % (prev_j["slug"], html.escape(prev_j["title"]))
                if prev_j else
                '<a class="prev" href="index.html"><span>返回</span>日常与照片</a>')
        right = ('<a class="next" href="%s.html"><span>下一篇</span>%s</a>'
                 % (next_j["slug"], html.escape(next_j["title"]))
                 if next_j else
                 '<a class="next" href="../notes/index.html"><span>继续</span>读读笔记</a>')
        body = header("journal", "%s · 王松林" % j["title"], j["excerpt"]) + """
        <div class="index_outer inner">
          <article class="article_detail">
            <div class="meta">{date} &middot; 日常</div>
            <h1 class="detail_head">{title}</h1>
            <p class="detail_lead">{excerpt}</p>
            <div class="body">{body}</div>
            <div class="detail_foot">
              {left}
              {right}
            </div>
          </article>
        </div>
""".format(
            date=j["date"], title=html.escape(j["title"]), excerpt=html.escape(j["excerpt"]),
            body=j["body"].strip(), left=left, right=right,
        )
        write("journal/%s.html" % j["slug"], body + FOOT.format(other=TRIP))


def write(rel, content):
    path = os.path.join(SITE, rel.replace("/", os.sep))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("  wrote", rel)


if __name__ == "__main__":
    build_notes_index()
    build_notes_detail()
    build_journal_index()
    build_journal_detail()
    print("done: %d notes, %d journal entries" % (len(NOTES), len(JOURNAL)))
