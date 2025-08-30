export default {
  namespaced: true,
  
  state: {
    phase: 'connecting',  // connecting, lobby, prompt_selection, submission, voting, results, game_over
    currentRound: 0,
    totalRounds: 0,
    players: [],
    currentTargets: [],
    submissions: {},
    selectedVote: null,
    scoreboard: []
  },
  
  mutations: {
    SET_PHASE(state, phase) {
      state.phase = phase
    },
    SET_ROUND_INFO(state, { current, total }) {
      state.currentRound = current
      state.totalRounds = total
    },
    SET_PLAYERS(state, players) {
      state.players = players
    },
    SET_TARGETS(state, targets) {
      state.currentTargets = targets
    },
    SET_SUBMISSIONS(state, submissions) {
      state.submissions = submissions
    },
    SET_SELECTED_VOTE(state, voteId) {
      state.selectedVote = voteId
    },
    SET_SCOREBOARD(state, scoreboard) {
      state.scoreboard = scoreboard
    }
  },
  
  actions: {
    updateGameState({ commit }, data) {
      if (data.phase) commit('SET_PHASE', data.phase)
      if (data.currentRound !== undefined && data.totalRounds !== undefined) {
        commit('SET_ROUND_INFO', { 
          current: data.currentRound, 
          total: data.totalRounds 
        })
      }
      if (data.players) commit('SET_PLAYERS', data.players)
    }
  }
}
