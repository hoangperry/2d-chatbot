from animte import Artist


def main():
    art = Artist(fps=120, character='science-1')
    reuslt = art.audio_to_video('news/tin-kinh-te-08-03-2023.wav', fps=120)
    print(reuslt)
    # a = GoogleDialogflowSession(cfg)
    # print(a)
    # print(a.chat('Hello bạn'))


if __name__ == '__main__':
    main()
