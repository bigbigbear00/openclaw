// Guard-rails pseudocode (phase-1): functions to implement in agent runtime

function pickWindowTurns(ctxLimit, longctx) {
  // choose windowTurns by nearest lower key in longctx.windowTurnsByCtx
}

function estimateTokens(textBlocks) {
  // call provider tokenizer if available; otherwise fallback to heuristic
}

function buildContext({system, instructions, user, s1, window, rag}) {
  // assemble pieces in priority order
}

function enforceBudget(ctxPieces, budget, longctx) {
  // deterministic removal: never remove system/user/s1
  // order: rag low-score -> window oldest -> truncate oversized chunks
}

async function summarizeToS2(messages, opts) {
  // call summarization model (small) with target tokens, return summary text
}

async function handleTelegramMessage(msg, session, agentId) {
  const model = resolveModelForAgent(agentId);
  const ctxLimit = getModelContextLimit(model);
  const reserve = Math.max(longctx.reserveMinTokens, Math.floor(ctxLimit * longctx.reserveRatio));
  const budget = ctxLimit - reserve;

  session.project_id = session.project_id || `tg:${msg.chat_id}`;
  if (!session.session_summary) session.session_summary = seedEmptyS1();

  const windowTurns = pickWindowTurns(ctxLimit, longctx);
  let windowMsgs = loadRecentTurns(session, windowTurns);
  let ragChunks = retrieveMemory({ project_id: session.project_id, query: msg.text, capTokens: longctx.ragCapTokens, chunkTargetTokens: longctx.chunkTargetTokens });

  let ctxPieces = buildContext({system: SYSTEM, instructions: INSTR, user: msg.text, s1: session.session_summary, window: windowMsgs, rag: ragChunks});
  let est = estimateTokens(ctxPieces);

  let compactionFlag = false;
  if (est > budget * longctx.yellowRatio) {
    // shrink window
    windowMsgs = shrinkWindow(windowMsgs);
    ctxPieces = buildContext({system: SYSTEM, instructions: INSTR, user: msg.text, s1: session.session_summary, window: windowMsgs, rag: ragChunks});
    est = estimateTokens(ctxPieces);
  }

  if (est > budget * longctx.redRatio) {
    compactionFlag = true;
    const evictMsgs = selectEvictableMessages(session, windowMsgs, session.summary_cursor_msg_id);
    if (evictMsgs.length > 0) {
      const s2 = await summarizeToS2(evictMsgs, {targetTokens: longctx.s2TargetTokens || 800});
      memory.upsert({ type: 'summary', project_id: session.project_id, session_id: session.id, source_range: range(evictMsgs), text: s2 });
      session.session_summary = updateS1(session.session_summary, s2, {targetTokens: longctx.s1TargetTokens});
      session.summary_cursor_msg_id = lastMsgId(evictMsgs);
      dropFromSessionHistory(session, evictMsgs);
      session.last_compaction_at = Date.now();
    }

    // rebuild
    windowMsgs = loadRecentTurns(session, windowTurns);
    ragChunks = retrieveMemory(...);
    ctxPieces = buildContext({system: SYSTEM, instructions: INSTR, user: msg.text, s1: session.session_summary, window: windowMsgs, rag: ragChunks});
    ctxPieces = enforceBudget(ctxPieces, budget, longctx);
  } else {
    ctxPieces = enforceBudget(ctxPieces, budget, longctx);
  }

  const reply = await callModel(model, ctxPieces);
  appendToSessionHistory(session, msg, reply);
  maybeWriteMetrics({est, model, compactionFlag});
  return reply;
}
