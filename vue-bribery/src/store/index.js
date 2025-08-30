import { createStore } from 'vuex'
import auth from './modules/auth'
import game from './modules/game'
import ui from './modules/ui'

export default createStore({
  modules: {
    auth,
    game,
    ui
  }
})
