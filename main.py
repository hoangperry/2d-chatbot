import hydra
from animte import Artist
from chatbot.session import GoogleDialogflowSession


@hydra.main(version_base=None, config_path='config', config_name="dialogflow")
def main(cfg):
    # art = Artist(fps=30)
    # art.text_to_animation(
    #     'Chào bạn'
    # )

    a = GoogleDialogflowSession(cfg)
    print(a)
    print(a.chat('Hello bạn'))


if __name__ == '__main__':
    main()
