import os
import json
import discord
from discord import app_commands
from dotenv import load_dotenv
import logging

# .env 파일에서 환경 변수 로드
load_dotenv()

# 디스코드 봇 설정
intents = discord.Intents.default()
intents.guilds = True  # 서버 목록 확인용

class NoticeBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.notice_channels = {}
        self.CHANNEL_CONFIG_FILE = 'channel_config.json'
        self.load_channel_config()

    async def setup_hook(self):
        """봇 시작시 실행되는 설정 훅"""
        try:
            print("슬래시 커맨드를 전역으로 등록합니다...")
            await self.tree.sync()
            print("슬래시 커맨드 등록 완료!")
        except Exception as e:
            print(f"슬래시 커맨드 등록 실패: {e}")

    def load_channel_config(self):
        """저장된 채널 설정을 불러옵니다."""
        try:
            if os.path.exists(self.CHANNEL_CONFIG_FILE):
                with open(self.CHANNEL_CONFIG_FILE, 'r') as f:
                    self.notice_channels = json.load(f)
        except Exception as e:
            print(f"채널 설정 로드 중 오류 발생: {e}")

    def save_channel_config(self):
        """채널 설정을 파일에 저장합니다."""
        try:
            with open(self.CHANNEL_CONFIG_FILE, 'w') as f:
                json.dump(self.notice_channels, f)
        except Exception as e:
            print(f"채널 설정 저장 중 오류 발생: {e}")

client = NoticeBot()

@client.event
async def on_ready():
    print(f'{client.user}로 로그인했습니다!')
    guild_count = len(client.guilds)
    print(f'봇이 {guild_count}개의 서버에 참여중입니다.')
    
    # 각 서버의 공지 채널 확인
    for guild in client.guilds:
        channel_id = client.notice_channels.get(str(guild.id))
        if channel_id:
            channel = client.get_channel(int(channel_id))
            if channel:
                print(f'서버 [{guild.name}]의 공지 채널: #{channel.name}')
            else:
                print(f'경고: 서버 [{guild.name}]의 설정된 채널을 찾을 수 없습니다.')
        else:
            print(f'경고: 서버 [{guild.name}]에 공지 채널이 설정되지 않았습니다.')

@client.tree.command(name="setchannel", description="공지사항을 받을 채널을 설정합니다")
@app_commands.checks.has_permissions(administrator=True)
async def set_channel(interaction: discord.Interaction, channel: discord.TextChannel = None):
    """공지사항을 받을 채널을 설정합니다."""
    # 채널이 지정되지 않은 경우 현재 채널 사용
    channel = channel or interaction.channel
    
    client.notice_channels[str(interaction.guild_id)] = str(channel.id)
    client.save_channel_config()
    await interaction.response.send_message(
        f'공지 채널이 {channel.mention}로 설정되었습니다.',
        ephemeral=True
    )

@client.tree.command(name="getchannel", description="현재 설정된 공지 채널을 확인합니다")
async def get_channel(interaction: discord.Interaction):
    """현재 설정된 공지 채널을 확인합니다."""
    channel_id = client.notice_channels.get(str(interaction.guild_id))
    if channel_id:
        channel = client.get_channel(int(channel_id))
        if channel:
            await interaction.response.send_message(
                f'현재 공지 채널: {channel.mention}',
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                '설정된 채널을 찾을 수 없습니다. 다시 설정해주세요.',
                ephemeral=True
            )
    else:
        await interaction.response.send_message(
            '공지 채널이 설정되지 않았습니다. /setchannel 명령어로 설정해주세요.',
            ephemeral=True
        )

@client.tree.command(name="testnotice", description="[디버그] 최근 공지사항을 테스트로 전송합니다")
@app_commands.checks.has_permissions(administrator=True)
async def test_notice(interaction: discord.Interaction):
    """[디버그] 최근 공지사항을 테스트로 전송합니다."""
    from rss_feed_checker import parse_feed, format_entry
    from notice_entry import NoticeEntry
    
    try:
        # 응답 먼저 보내기 (3초 제한 때문)
        await interaction.response.send_message(
            "공지사항 테스트를 시작합니다...",
            ephemeral=True
        )
        
        # RSS 피드에서 최신 글 가져오기
        RSS_URL = os.getenv('RSS_FEED_URL', 'https://cs.kookmin.ac.kr/news/notice/rss')
        entries = parse_feed(RSS_URL)
        
        if not entries:
            await interaction.followup.send(
                "RSS 피드에서 공지사항을 가져올 수 없습니다.",
                ephemeral=True
            )
            return
            
        # 최신 글 변환
        entry_data = format_entry(entries[0])
        notice = NoticeEntry(entry_data)
        
        # 현재 채널에만 전송
        embed = discord.Embed(
            title=f"[테스트] {notice.title}",
            url=notice.link,
            color=discord.Color.orange()
        )
        embed.add_field(name="작성일", value=notice.published.strftime('%Y-%m-%d %H:%M:%S'), inline=False)
        embed.set_footer(text="이것은 테스트 메시지입니다")
        
        await interaction.channel.send(embed=embed)
        
        await interaction.followup.send(
            "테스트 공지사항이 전송되었습니다.",
            ephemeral=True
        )
        
    except Exception as e:
        await interaction.followup.send(
            f"테스트 중 오류가 발생했습니다: {str(e)}",
            ephemeral=True
        )

async def send_notice(notice):
    """모든 서버의 설정된 공지 채널에 공지사항을 전송합니다."""
    try:
        # 서버 목록 새로 가져오기
        await client.wait_until_ready()  # 봇이 완전히 준비될 때까지 대기
        guilds = client.guilds
        
        for guild in guilds:
            channel_id = client.notice_channels.get(str(guild.id))
            if channel_id:
                channel = guild.get_channel(int(channel_id))  # guild.get_channel 사용
                if channel:
                    embed = discord.Embed(
                        title=notice.title,
                        url=notice.link,
                        color=discord.Color.blue()
                    )
                    embed.add_field(name="작성일", value=notice.published.strftime('%Y-%m-%d'), inline=False)
                    try:
                        await channel.send(embed=embed)
                        print(f'서버 [{guild.name}]에 공지사항을 전송했습니다: {notice.title}')
                    except discord.errors.Forbidden:
                        print(f'서버 [{guild.name}]의 채널에 메시지를 보낼 권한이 없습니다.')
                    except Exception as e:
                        print(f'서버 [{guild.name}] 메시지 전송 중 오류: {e}')
                else:
                    print(f'서버 [{guild.name}]의 설정된 채널을 찾을 수 없습니다.')
            else:
                print(f'서버 [{guild.name}]에 공지 채널이 설정되지 않았습니다.')
    except Exception as e:
        print(f"디스코드 메시지 전송 중 오류 발생: {e}")

@client.event
async def on_guild_join(guild):
    """봇이 새로운 서버에 참여했을 때 실행됩니다."""
    logging.info(f'새로운 서버 [{guild.name}]에 참여했습니다.')
    try:
        await client.tree.sync(guild=guild)
        logging.info(f'서버 [{guild.name}]에 슬래시 커맨드를 등록했습니다.')
        
        # 서버의 감사 로그에서 봇 초대 이벤트를 찾아 초대한 사람에게만 메시지 전송
        async for entry in guild.audit_logs(action=discord.AuditLogAction.bot_add, limit=1):
            if entry.target.id == client.user.id:  # 이 봇을 초대한 이벤트인지 확인
                try:
                    embed = discord.Embed(
                        title="국민대학교 공지사항 알리미 봇",
                        description="공지사항을 받을 채널을 설정하려면 `/setchannel` 명령어를 사용해주세요.",
                        color=discord.Color.blue()
                    )
                    await entry.user.send(embed=embed)
                    logging.info(f'서버 [{guild.name}]에서 봇을 초대한 {entry.user.name}에게 안내 메시지를 전송했습니다.')
                except:
                    logging.warning(f'서버 [{guild.name}]에서 봇을 초대한 {entry.user.name}에게 DM을 보낼 수 없습니다.')
                break
                    
    except Exception as e:
        logging.error(f'서버 [{guild.name}]에 슬래시 커맨드 등록 실패: {e}')

def run_bot():
    client.run(os.getenv('DISCORD_TOKEN')) 