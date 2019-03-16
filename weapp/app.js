//app.js
var protobuf = require('./weichatPb/protobuf.js');
var wordConfig = require('./wordProto.js');
var wordRoot = protobuf.Root.fromJSON(wordConfig);
var WordList = wordRoot.lookupType("WordList");
var WordDetail = wordRoot.lookupType("WordDetail");
var WordBrief = wordRoot.lookupType("WordBrief");
var ChnDetail = wordRoot.lookupType("ChnDetail");

const audio = wx.createInnerAudioContext();

App({

  globalData: {
    userInfo: null,
    WordList: WordList,
    WordBrief: WordBrief,
    WordDetail: WordDetail,
    ChnDetail: ChnDetail,
    audio: audio
  },
  updateHistory: function(wordBrief, isClickedFromHistory) {
    //console.log(isClickedFromHistory)
    let historyList = this.globalData.historyList;
    for (let i = 0; i < historyList.length; i++) {
      if (historyList[i].wordOut === wordBrief.wordOut) {
        //如果该单词已经存在于历史记录中，则删去该单词
        historyList.splice(i, 1);
        break;
      }
    }
    historyList.unshift(wordBrief);
    wx.setStorage({
      key: 'historyList',
      data: historyList,
    })
    this.globalData.historyList = historyList;
    if (isClickedFromHistory === 'true')
      getCurrentPages()[0].setData({
        wordList: historyList
      })

  },
  clearHistory: function() {
    this.globalData.historyList = []
    wx.clearStorage()

  },
  onLaunch: function() {
    const updateManager = wx.getUpdateManager()
    updateManager.onUpdateReady(function() {
      wx.showModal({
        title: '更新提示',
        content: '新版本已经准备好，是否马上重启小程序？',
        success: function(res) {
          if (res.confirm) {
            // 新的版本已经下载好，调用 applyUpdate 应用新版本并重启
            updateManager.applyUpdate()
          }
        }
      })
    })
    updateManager.onUpdateFailed(function() {
      // 新的版本下载失败
    })
    //计算屏幕高度
    var that = this;
    wx.getSystemInfo({
      success: function(res) {
        that.globalData.windowHeight = res.windowHeight;
      }
    })
    wx.getStorage({
      key: 'historyList',
      success: function(res) {
        that.globalData.historyList = res.data;
      },
      fail: function() {
        that.globalData.historyList = [];

      }
    })
  }



})