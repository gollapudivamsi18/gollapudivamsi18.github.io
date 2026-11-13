/* Conversation engine for Vamsikrishna's Portfolio AI Assistant.
 *
 * Pure logic, no DOM: it runs in the browser and in Node (for tests).
 * Answers come only from the knowledge base; when nothing matches, the
 * assistant says so instead of guessing.
 *
 * Matching: each topic has keywords (single words or phrases). A question is
 * normalised, then scored: phrase hits count more than word hits, and topic
 * titles add a little. Follow-ups ("tell me more", "what about it", "how?")
 * reuse the topic currently in focus and walk through its extra detail.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.AssistantCore = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  var STOP = ("a an the is are was were be been of to in on for and or with about does did do " +
    "he his him what which how why when where can could would you your me my i tell please " +
    "any some has have had there this that it its at as by from more much many").split(" ");
  var STOPSET = {};
  STOP.forEach(function (w) { STOPSET[w] = true; });

  // Broad words that appear in many questions; a specific technology should win over them.
  var GENERIC = { experience: 1, background: 1, history: 1, career: 1, work: 1, worked: 1, roles: 1, years: 1, now: 1, current: 1, currently: 1 };

  var FOLLOW_UP = /^(tell me more|more|go on|continue|and\??|what else|anything else|details?|more details|elaborate|explain more|explain|expand|keep going|next)\b|\b(more about (it|that|this)|about (it|that|this)|that one|the same)\b/;
  var PRONOUN_ONLY = /^(how|why|what|which|where|when)\b.*\b(it|that|this|those|them)\b/;
  var GREETING = /^(hi|hello|hey|good (morning|afternoon|evening)|namaste)\b/;
  var THANKS = /^(thanks|thank you|thx|cheers|great|ok thanks|okay thanks)\b/;
  var BYE = /^(bye|goodbye|see you|that's all|thats all)\b/;

  function normalise(text) {
    return String(text || "").toLowerCase()
      .replace(/[’']/g, "'")
      .replace(/[^a-z0-9+#./\- ']/g, " ")
      .replace(/\s+/g, " ").trim();
  }

  function words(text) {
    return normalise(text).split(" ").filter(function (w) { return w && !STOPSET[w]; });
  }

  function scoreTopic(topic, norm, tokens) {
    var score = 0;
    var padded = " " + norm + " ";
    topic.keywords.forEach(function (k) {
      var kw = normalise(k);
      if (!kw) return;
      if (kw.indexOf(" ") >= 0 || kw.indexOf("-") >= 0) {
        if (padded.indexOf(" " + kw + " ") >= 0 || norm.indexOf(kw) >= 0) score += 3 + kw.split(" ").length;
      } else if (tokens.indexOf(kw) >= 0) {
        score += GENERIC[kw] ? 1 : 2;
      } else if (kw.length > 4 && tokens.some(function (t) { return t.length > 4 && (t.indexOf(kw) === 0 || kw.indexOf(t) === 0); })) {
        score += 1; // plural / stem, e.g. "pipelines" vs "pipeline"
      }
    });
    words(topic.title).forEach(function (w) { if (tokens.indexOf(w) >= 0) score += 0.5; });
    return score;
  }

  function Conversation(kb) {
    if (!kb || !Array.isArray(kb.topics)) throw new Error("knowledge base missing topics");
    this.kb = kb;
    this.byId = {};
    var self = this;
    kb.topics.forEach(function (t) { self.byId[t.id] = t; });
    this.reset();
  }

  Conversation.prototype.reset = function () {
    this.focus = null;      // topic id currently being discussed
    this.depth = 0;         // how many "more" items of the focus topic were shown
    this.turns = 0;
  };

  Conversation.prototype.suggest = function (topic) {
    var self = this;
    return (topic ? topic.related : ["intro", "skills", "availability", "projects"])
      .map(function (id) { return self.byId[id]; })
      .filter(Boolean)
      .map(function (t) { return { id: t.id, label: t.title }; });
  };

  Conversation.prototype.answerTopic = function (topic, viaFollowUp) {
    var text;
    if (viaFollowUp && this.focus === topic.id) {
      if (this.depth < topic.more.length) {
        text = topic.more[this.depth];
        this.depth += 1;
      } else {
        text = "That's everything I have on " + topic.title.toLowerCase() +
          ". You could ask about one of the related topics below.";
      }
    } else {
      this.focus = topic.id;
      this.depth = 0;
      text = topic.answer;
    }
    var hasMore = this.focus === topic.id && this.depth < topic.more.length;
    return { text: text, topic: topic.id, title: topic.title, hasMore: hasMore, suggestions: this.suggest(topic) };
  };

  /* Main entry point. Accepts free text or {topic: id} from a suggestion chip. */
  Conversation.prototype.ask = function (input) {
    this.turns += 1;
    if (input && typeof input === "object" && input.topic) {
      var chosen = this.byId[input.topic];
      if (chosen) return this.answerTopic(chosen, false);
    }
    var norm = normalise(input);
    if (!norm) {
      return { text: "Please type or say a question.", topic: null, hasMore: false, suggestions: this.suggest(null) };
    }
    var small = this.kb.smalltalk || {};
    if (GREETING.test(norm) && norm.split(" ").length <= 4) {
      return { text: small.greeting, topic: null, hasMore: false, suggestions: this.suggest(null) };
    }
    if (THANKS.test(norm) && norm.split(" ").length <= 4) {
      return { text: small.thanks, topic: null, hasMore: false, suggestions: this.suggest(this.byId[this.focus]) };
    }
    if (BYE.test(norm)) {
      return { text: small.bye, topic: null, hasMore: false, suggestions: [] };
    }

    var tokens = words(norm);
    var best = null, bestScore = 0, second = 0;
    var self = this;
    this.kb.topics.forEach(function (t) {
      var s = scoreTopic(t, norm, tokens);
      // Slight preference for the topic in focus, so follow-up questions that
      // share a keyword with it stay in the same thread.
      if (t.id === self.focus && s > 0) s += 0.75;
      if (s > bestScore) { second = bestScore; bestScore = s; best = t; }
      else if (s > second) { second = s; }
    });

    var isFollowUp = FOLLOW_UP.test(norm) || (PRONOUN_ONLY.test(norm) && bestScore < 2);
    if (isFollowUp && this.focus && (bestScore < 2 || (best && best.id === this.focus))) {
      return this.answerTopic(this.byId[this.focus], true);
    }
    if (best && bestScore >= 1.5) {
      return this.answerTopic(best, false);
    }
    if (isFollowUp && !this.focus) {
      return { text: "Happy to go into more detail. Which topic? For example his SRE work, CI/CD, Kubernetes or a specific demo.", topic: null, hasMore: false, suggestions: this.suggest(null) };
    }
    return { text: this.kb.fallback, topic: null, hasMore: false, suggestions: this.suggest(null) };
  };

  return { Conversation: Conversation, normalise: normalise, words: words, scoreTopic: scoreTopic };
});
