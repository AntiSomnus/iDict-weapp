//获取应用实例
const app = getApp()
var WordList = app.globalData.WordList;
var WordDetail = app.globalData.WordDetail;
var WordBrief = app.globalData.WordBrief;
var baseUrl = 'https://ireading.site/'

const sourceDict = {
  0: "牛津高阶英汉双解词典",
  1: "剑桥高阶英汉双解词典",
  2: "朗文当代高级英语辞典",
  3: "柯林斯英汉双解大词典 ",
  4: "金山词霸在线词典"
}

const {
  $Toast
} = require('../../dist/base/index');

var feedback = {};
var defaultFeedbackWord = '';
var wordNotCollected = false;

function replaceAll(str, find, replace) {
  return str.replace(new RegExp(find, 'g'), replace);
}

function modifiedStrToList(modifiedStr) {
  return modifiedStr.split(/(&nbsp;)|([a-zA-z][a-zA-z-']*)/g).filter(function(n) {
    return n
  });

}

Page({
  data: {
    detailedWord: null,
    maxSentNumber: [10, 10, 10, 10, 10],
    feedbackSectionArray: [
      "内容有误",
      "尚未收录",
      "其他问题",
      "产品建议",
    ],
    feedbackSectionIndex: 0,
    sourceIndex: 0,
    windowHeight: app.globalData.windowHeight
  },


  onLoad: function(param) {

    this.myaudio = wx.createAudioContext('myAudio')

    var that = this;
    wx.request({
      url: baseUrl + 'word/detail',
      responseType: "arraybuffer",
      data: {
        'word': param.word,
      },
      header: {
        "Content-Type": "application/text"
      },
      success: function(res) {
        if (res.statusCode === 200) {
          let wordDetail = WordDetail.decode(new Uint8Array(res.data))
          let engList = []
          let engDefList = []
          let sourceArray = []
          let eng_str = ''
          if (wordDetail.wordBrief.engDefinitions) {
            let engDefinitions = wordDetail.wordBrief.engDefinitions
            for (var i = 0; i < engDefinitions.length; i++) {
              //对所有英语释义
              eng_str = replaceAll(engDefinitions[i].meaning, ' ', '&nbsp;');
              engDefList.push(modifiedStrToList(eng_str));
            }
          }
          if (wordDetail.sentenceLists) {
            for (var l = 0; l < wordDetail.sentenceLists.length; l++) {
              //对每一个分类
              let sentenceList = wordDetail.sentenceLists[l];
              eng_str = '';
              let engCataList = []
              sourceArray.push(sourceDict[sentenceList.source])
              for (var i = 0; i < sentenceList.sentences.length; i++) {
                //对改分类下的所有例句
                eng_str = replaceAll(sentenceList.sentences[i].eng, ' ', '&nbsp;');
                engCataList.push(modifiedStrToList(eng_str));
              }
              engList.push(engCataList)
            }

          }
          defaultFeedbackWord = wordDetail.wordBrief.wordOut
          that.setData({
            isLoadingFinished: true,
            detailedWord: wordDetail,
            engList: engList,
            engDefList: engDefList,
            sourceArray: sourceArray
          })
          app.updateHistory(wordDetail.wordBrief,param.isHistoryShow)
        } else { //error
          defaultFeedbackWord = param.word
          wordNotCollected = true;
          that.setData({
            isLoadingFinished: true,
            errorInfo: {
              word: param.word,
              msg: "抱歉，暂无该单词释义"
            }
          })
        }

      }
    })

  },
  feedbackSectionChange: function(e) {
    this.setData({
      feedbackSectionIndex: e.detail.value
    })
  },
  sourceChange: function(e) {
    this.setData({
      sourceIndex: e.detail.value
    })
  },
  audioClicked: function(e) {
    this.setData({
      src: e.target.dataset.src
    })
    this.myaudio.play();
  },
  wordClickedInWordDetail: function(e) {
    var data = e.target.dataset;
    var that = this;
    var word = data.word;
    if (/^([a-zA-Z][a-zA-z-']*)$/.test(e.target.dataset.word) && word) {
      var currentClickedWord = {};
      currentClickedWord.indexSent = data.indexSent;
      currentClickedWord.indexWord = data.indexWord;
      currentClickedWord.section = data.section;
      currentClickedWord.word = word;
      this.setData({
        currentClickedWord: currentClickedWord,
      });
      wx.request({
        url: baseUrl + 'word/brief',
        responseType: "arraybuffer",
        data: {
          'word': word,
        },
        header: {
          "Content-Type": "application/text"
        },
        responseType: "arraybuffer",

        success: function(res) {
          var currentClickedWordInfo = {}
          if (res.statusCode === 200) {
            currentClickedWordInfo = WordBrief.decode(new Uint8Array(res.data));
          } else {
            currentClickedWordInfo.notCollected = true;
            currentClickedWordInfo.wordOut = word;
            currentClickedWordInfo.chnDefinitions = []
            currentClickedWordInfo.chnDefinitions[0] = {}
            currentClickedWordInfo.chnDefinitions[0].meaning = "暂未被收录"
          }
          that.setData({
            isShowWordInDetail: true,
            currentClickedWordInfo: currentClickedWordInfo
          })
        }
      })
    }


  },
  loadMoreSent: function() {
    let ar = this.data.maxSentNumber;
    ar[this.data.sourceIndex] += 10;
    this.setData({
      maxSentNumber: ar
    })
  },
  detailOutClicked: function() {
    this.setData({
      isShowWordInDetail: false,
      currentClickedWord: {},
    });
  },
  feedbackOutClicked: function(e) {
    if (e.target.id === 'overlay')
      this.setData({
        isFeedbackShow: false,
      });
  },
  longTapToWordDetail: function() {
    let popupWord = this.data.currentClickedWordInfo.wordOut;
    let detailedWord = this.data.detailedWord.wordBrief.wordOut;
    if (popupWord !== detailedWord)
      wx.navigateTo({
        url: '../word-detail/word-detail?word=' + this.data.currentClickedWordInfo.wordOut,
      })
  },
  onReachBottom: function() {
    let ar = this.data.maxSentNumber;
    ar[this.data.sourceIndex] += 10;
    this.setData({
      maxSentNumber: ar
    }, 100)
  },
  feedbackClicked: function(e) {
    feedback.word = e.target.dataset.type ? this.data.currentClickedWordInfo.wordOut : defaultFeedbackWord;
    feedback.content = '';
    this.setData({
      feedbackWord: feedback.word,
      feedbackSectionIndex: e.target.dataset.type || wordNotCollected ? 1 : 0,
      isFeedbackShow: true
    })
  },
  inputFeedbackWord: function(e) {
    feedback.word = e.detail.value

  },
  feedbackContentInput: function(e) {
    feedback.content = e.detail.value
  },
  feedbackSubmit: function() {
    var that = this;
    wx.request({
      url: baseUrl + 'support/',
      method: "POST",
      data: {
        'type': this.data.feedbackSectionIndex,
        'details': feedback.word + '\r\n' + feedback.content
      },
      header: {
        "Content-Type": "application/x-www-form-urlencoded"
      },
      success: function(res) {
        $Toast({
          content: '提交成功',
          type: 'success'
        });
        that.setData({
          isFeedbackShow: false,
          feedbackContent: '',
        })
      },
      fail: function(res) {
        $Toast({
          content: '提交失败',
          type: 'error'
        });
      }
    })

  }

})