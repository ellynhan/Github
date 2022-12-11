import datetime
import datetime as dt
from github import Github

g = Github("token")
repo = g.get_repo("ellynhan/challenge100-codingtest-study")
#test_repo = g.get_repo("ellynhan/Github")
participants = dict()


def get_n_merge_pulls():
    pulls = repo.get_pulls(state='open', sort='created')
    ret = []
    for pr in pulls:
        num_str = pr.title.replace(" ", "").split('/')[-1]
        num = ""
        for c in num_str:
            if c.isdigit():
                num = num + c
        if num != "":
            print(pr.user.login)
            ret.append([pr.user.login,  int(num)])
            if pr.user.login not in participants:
                participants[pr.user.login] = {'avatar': pr.user.avatar_url, 'link': pr.user.html_url, 'count': 0}
            pr.merge()

    for e in ret:
        participants[e[0]]['count'] += e[1]


def check_contributors(readme):
    contrib_pos = readme.find("-orange.svg")
    contrib_cnt = 1
    while readme[contrib_pos - contrib_cnt].isdigit():
        contrib_cnt += 1
    return readme[:contrib_pos - contrib_cnt] + str(repo.get_contributors().totalCount) + readme[contrib_pos:]
    #이 함수 수정 필요. contributors-43이렇게 나와야하는데 contribut43 이렇게 나왔음


def get_current_count(readme, login): #나중에 완성하고서 구현할것.
    num = ""
    target = f'{login}</b><br><img src="https://us-central1-progress-markdown.cloudfunctions.net/progress/'
    target_pos = readme.find(target)
    while readme[target_pos + len(target)].isdigit():
        num += readme[target_pos + len(target)]
        target_pos += 1
    return int(num) if num != "" else 0


def get_participants(readme):
    contributors = repo.get_stats_contributors()
    for contributor in contributors:
        contrib = contributor.author
        participants.update({contrib.login:{'avatar':contrib.avatar_url, 'link':contrib.html_url, 'count': get_current_count(readme, contrib.login)}})


def td_format(link, avatar, user_id, count):
    progress = ""
    if count > 99:
        user_id = '🎉'+user_id

    if count == 0:
        progress = "중도포기"
    else:
        progress = f'<img src="https://us-central1-progress-markdown.cloudfunctions.net/progress/{count}"/>'

    return f' \
        <td align="center"><a href="{link}"><img src="{avatar}?s=100" width="100px;" alt=""/> \
        <br /><sub><b>{user_id}</b><br>{progress}</sub></a><br /></td>\n'


def edit_table(readme):
    ret = ""
    phase = 0
    td_cnt = 0
    phase_up = True
    title = ['### 🎉 챌린지 달성 🎉', '### 🔥 챌린지 도전 🔥', '### 💀 챌린지 포기 💀']
    global participants
    participants = sorted(participants.items(), key=lambda item: item[1]['count'], reverse=True)

    for p in participants:
        user_id = p[0]
        value = p[1]

        if (phase == 1 and value['count'] < 100) or (phase == 2 and value['count'] == 0):
            ret += '</table><br />\n\n'
            phase_up = True
            td_cnt = 0

        if phase_up:
            ret += title[phase] + "\n<table>"
            phase += 1
            phase_up = False

        if td_cnt == 0:
            ret += '<tr>'
        td_cnt += 1
        ret += td_format(value['link'], value['avatar'], user_id, value['count'])
        if td_cnt >= 7:
            ret += '</tr>'
            td_cnt = 0

    ret += '</table><br />\n\n'
    return ret


def get_week_no():
    '''
     -  -  -  -    1  2  3    -> 1 주차
     4  5  6  7  | 8  9  10   -> 2 주차
     11 12 13 14 | 15 16 17   -> 3 주차
     18 19 20 21 | 22 23 24   -> 4 주차
     25 26 27 28 | 29 30  -    -> 5 주차
    '''
    #해당 주차의 목요일을 기준으로 1주차인지 5주차인지 계산할 것
    today = dt.datetime.now()
    thursday = today - datetime.timedelta(days=3)
    first = dt.datetime.strptime(thursday.strftime("%Y-%m-01"), "%Y-%m-%d")
    if first.weekday() in (3,4,5):
        print(thursday.day//7+1)
    elif first.weekday() == 6:
        print((thursday.day-1)//7+1)
    else:
        print((thursday.day)) #아 어려워.. 다음에 계산하겠음


def get_commit_msg():
    today = dt.datetime.now()
    thursday = today - datetime.timedelta(days=3)
    return f'{today.strftime("%y년 %m월 %d일")} - {thursday.isocalendar().week}주차 업데이트 완료'


def edit_readme(readme):
    new_status = edit_table(readme)
    edit_point = "## ✅ 참여자와 진행도"
    status_pos = readme.find(edit_point)
    readme = readme[:status_pos+len(edit_point)+1] + new_status
    repo.update_file("README.md", get_commit_msg(), readme, file.sha)


if __name__ == "__main__":
    get_commit_msg()
    file = repo.get_contents("README.md")
    decode = file.decoded_content.decode('utf-8', 'strict')
    get_participants(decode)
    get_n_merge_pulls()
    decode = check_contributors(decode)
    edit_readme(decode)
