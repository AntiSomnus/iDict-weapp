module.exports = {
    "nested": {
        "WordList": {
            "fields": {
                "wordBriefs": {
                    "rule": "repeated",
                    "type": "WordBrief",
                    "id": 1
                },
                "wordSuggestions": {
                    "rule": "repeated",
                    "type": "WordBrief",
                    "id": 2
                }
            }
        },
        "WordBrief": {
            "fields": {
                "wordIn": {
                    "type": "string",
                    "id": 1
                },
                "wordOut": {
                    "type": "string",
                    "id": 2
                },
                "ukPron": {
                    "type": "Pronunciation",
                    "id": 3
                },
                "usPron": {
                    "type": "Pronunciation",
                    "id": 4
                },
                "chnDefinitions": {
                    "rule": "repeated",
                    "type": "Definition",
                    "id": 5
                },
                "engDefinitions": {
                    "rule": "repeated",
                    "type": "Definition",
                    "id": 6
                },
                "tags": {
                    "rule": "repeated",
                    "type": "bool",
                    "id": 7
                },
                "lemma": {
                    "type": "Lemma",
                    "id": 8
                }
            },
            "nested": {
                "Pronunciation": {
                    "fields": {
                        "ps": {
                            "type": "string",
                            "id": 1
                        },
                        "url": {
                            "type": "string",
                            "id": 2
                        }
                    }
                },
                "Definition": {
                    "fields": {
                        "pos": {
                            "type": "string",
                            "id": 1
                        },
                        "meaning": {
                            "type": "string",
                            "id": 2
                        }
                    }
                },
                "Lemma": {
                    "fields": {
                        "lemma": {
                            "type": "string",
                            "id": 1
                        },
                        "relation": {
                            "type": "string",
                            "id": 2
                        }
                    }
                }
            }
        },
        "WordDetail": {
            "fields": {
                "wordBrief": {
                    "type": "WordBrief",
                    "id": 1
                },
                "collins": {
                    "type": "int32",
                    "id": 2
                },
                "bnc": {
                    "type": "int32",
                    "id": 3
                },
                "frq": {
                    "type": "int32",
                    "id": 4
                },
                "sentenceLists": {
                    "rule": "repeated",
                    "type": "SentenceList",
                    "id": 5
                },
                "derivatives": {
                    "rule": "repeated",
                    "type": "Derivative",
                    "id": 6
                }
            },
            "nested": {
                "SentenceList": {
                    "fields": {
                        "source": {
                            "type": "Source",
                            "id": 1
                        },
                        "sentences": {
                            "rule": "repeated",
                            "type": "Sentence",
                            "id": 2
                        }
                    },
                    "nested": {
                        "Source": {
                            "values": {
                                "OXFORD": 0,
                                "CAMBRIDGE": 1,
                                "LONGMAN": 2,
                                "COLLINS": 3,
                                "ONLINE": 4
                            }
                        },
                        "Sentence": {
                            "fields": {
                                "eng": {
                                    "type": "string",
                                    "id": 1
                                },
                                "chn": {
                                    "type": "string",
                                    "id": 2
                                }
                            }
                        }
                    }
                },
                "Derivative": {
                    "fields": {
                        "word": {
                            "type": "string",
                            "id": 1
                        },
                        "relation": {
                            "type": "string",
                            "id": 2
                        }
                    }
                }
            }
        }
    }
}