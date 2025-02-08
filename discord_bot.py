import os
import json
import discord
from discord import app_commands
from dotenv import load_dotenv
from crawler_manager import CrawlerConfig, CrawlerType

# .env 파일에서 환경 변수 로드
load_dotenv()

# 디스코드 봇 설정
intents = discord.Intents.default()
intents.guilds = True  # 서버 목록 확인용
intents.dm_messages = True  # DM 메시지 허용

class NoticeBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.crawler_config = CrawlerConfig()

    async def setup_hook(self):
        """봇 시작시 실행되는 설정 훅"""
        try:
            print("슬래시 커맨드를 전역으로 등록합니다...")
            await self.tree.sync()
            print("슬래시 커맨드 등록 완료!")
        except Exception as e:
            print(f"슬래시 커맨드 등록 실패: {e}")

client = NoticeBot()

@client.event
async def on_ready():
    print(f'{client.user}로 로그인했습니다!')
    guild_count = len(client.guilds)
    print(f'봇이 {guild_count}개의 서버에 참여중입니다.')

@client.tree.command(name="testnotice", description="[디버그] 선택한 크롤러의 최근 공지사항을 테스트로 전송합니다")
@app_commands.choices(crawler=[
    app_commands.Choice(name="SW학사공지", value="swAcademic"),
    app_commands.Choice(name="SW중심대학공지", value="sw"),
])
async def test_notice(
    interaction: discord.Interaction, 
    crawler: str
):
    """[디버그] 선택한 크롤러의 최근 공지사항을 테스트로 전송합니다."""
    
    # DM 채널인지 확인
    is_dm = isinstance(interaction.channel, discord.DMChannel)
    
    # 서버 채널이고 관리자 권한이 없는 경우에만 권한 체크
    if not is_dm and not interaction.permissions.administrator:
        await interaction.response.send_message(
            "이 명령어는 관리자 권한이 필요합니다.",
            ephemeral=True
        )
        return
        
    try:
        # 응답 먼저 보내기 (3초 제한 때문)
        await interaction.response.send_message(
            f"{crawler} 테스트를 시작합니다...",
            ephemeral=True
        )
        
        if crawler == "swAcademic":
            # RSS 피드에서 최신 글 가져오기
            from rss_feed_checker import parse_feed, format_entry
            from notice_entry import NoticeEntry  # NoticeEntry import 추가
            
            RSS_URL = os.getenv('SWACADEMIC_RSS_URL', 'https://cs.kookmin.ac.kr/news/notice/rss')
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
        else:  # sw 크롤러
            from sw_notice_checker import SWNoticeChecker
            
            checker = SWNoticeChecker()
            notices = await checker.check_new_notices()
            
            if not notices:
                await interaction.followup.send(
                    "새로운 SW중심대학 공지사항이 없습니다.",
                    ephemeral=True
                )
                return
                
            notice = notices[0]  # 최신 공지사항
        
        # 현재 채널에 테스트 메시지 전송
        embed = discord.Embed(
            title=f"[테스트] {notice.title}",
            url=notice.link,
            color=discord.Color.orange()
        )
            
        embed.set_footer(text=f"이것은 {crawler} 테스트 메시지입니다")

        print(f"테스트 메시지 전송: {notice.title}")
        
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

@client.tree.command(name="공지등록", description="현재 채널에 공지사항 알림을 등록합니다")
@app_commands.choices(type=[
    app_commands.Choice(name="SW학사공지", value="swAcademic"),
    app_commands.Choice(name="SW중심대학공지", value="sw")
])
async def register_notice(interaction: discord.Interaction, type: str):
    """현재 채널에 선택한 유형의 공지사항 알림을 등록합니다. (DM에서도 사용 가능)"""
    channel = interaction.channel
    
    # DM 채널인지 확인
    is_dm = isinstance(channel, discord.DMChannel)
    
    if not is_dm:  # 서버 채널인 경우
        # 관리자 권한 확인
        if not interaction.permissions.administrator:
            await interaction.response.send_message(
                "이 명령어는 관리자 권한이 필요합니다.",
                ephemeral=True
            )
            return
            
        # 봇의 권한 확인
        permissions = channel.permissions_for(channel.guild.me)
        if not permissions.send_messages or not permissions.embed_links:
            await interaction.response.send_message(
                "이 채널에 메시지를 보낼 권한이 없습니다. 봇에게 '메시지 보내기'와 '임베드 링크' 권한을 부여해주세요.",
                ephemeral=True
            )
            return

    # 크롤러 타입 매핑
    crawler_type_map = {
        "swAcademic": CrawlerType.SWACADEMIC,
        "sw": CrawlerType.SW
    }
    
    # 공지 타입 한글명 매핑
    notice_type_names = {
        "swAcademic": "SW학사공지",
        "sw": "SW중심대학공지"
    }

    channel_id = str(interaction.channel_id)
    if client.crawler_config.add_crawler(channel_id, crawler_type_map[type]):
        await interaction.response.send_message(
            f"이 채널에 {notice_type_names[type]} 알림이 등록되었습니다.",
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            f"이 채널은 이미 {notice_type_names[type]} 알림이 등록되어 있습니다.",
            ephemeral=True
        )

@client.tree.command(name="등록된공지", description="현재 채널에 등록된 알림 목록을 확인합니다")
async def list_notifications(interaction: discord.Interaction):
    """현재 채널에 등록된 알림 목록을 확인합니다."""
    channel_id = str(interaction.channel_id)
    crawlers = client.crawler_config.get_channel_crawlers(channel_id)
    
    if not crawlers:
        await interaction.response.send_message(
            "이 채널에 등록된 알림이 없습니다.",
            ephemeral=True
        )
        return

    crawler_names = {
        "swAcademic": "SW학사공지",
        "sw": "SW중심대학공지"
    }
    
    message = "현재 등록된 알림 목록:\n"
    for crawler in crawlers:
        message += f"- {crawler_names.get(crawler, crawler)}\n"
    
    await interaction.response.send_message(message, ephemeral=True)

async def send_notice(notice, crawler_type: CrawlerType):
    """특정 크롤러의 공지사항을 해당하는 모든 채널에 전송합니다."""

    try:
        await client.wait_until_ready()
        
        channels = client.crawler_config.get_channels_for_crawler(crawler_type)
        for channel_id in channels:
            try:
                # 채널 또는 DM 가져오기
                channel = client.get_channel(int(channel_id))
                if not channel:  # 서버 채널이 아니면 DM 채널일 수 있음
                    try:
                        user = await client.fetch_user(int(channel_id))
                        channel = user.dm_channel
                        if not channel:
                            channel = await user.create_dm()
                    except:
                        print(f'사용자 ID {channel_id}를 찾을 수 없습니다.')
                        continue
                
                # 서버 채널인 경우 권한 확인
                if not isinstance(channel, discord.DMChannel):
                    permissions = channel.permissions_for(channel.guild.me)
                    if not permissions.send_messages or not permissions.embed_links:
                        print(f'채널 [{channel.name}]에 메시지를 보낼 권한이 없습니다.')
                        continue

                embed = discord.Embed(
                    title=notice.title,
                    url=notice.link,
                    color=discord.Color.blue()
                )
                
                if notice.published.year > 1970:
                    embed.add_field(name="작성일", value=notice.published.strftime('%Y-%m-%d'), inline=False)
                
                await channel.send(embed=embed)
                print(f'채널 [{getattr(channel, "name", "DM")}]에 공지사항을 전송했습니다: {notice.title}')
                
            except discord.Forbidden:
                print(f'채널 [{getattr(channel, "name", "DM")}]에 메시지를 보낼 권한이 없습니다.')
            except discord.NotFound:
                print(f'채널 ID {channel_id}가 존재하지 않습니다.')
            except Exception as e:
                print(f'채널 [{channel_id}] 메시지 전송 중 오류: {str(e)}')
    except Exception as e:
        print(f"디스코드 메시지 전송 중 오류 발생: {e}")

@client.event
async def on_guild_join(guild):
    """봇이 새로운 서버에 참여했을 때 실행됩니다."""
    print(f'새로운 서버 [{guild.name}]에 참여했습니다.')
    try:
        await client.tree.sync(guild=guild)
        print(f'서버 [{guild.name}]에 슬래시 커맨드를 등록했습니다.')
    except Exception as e:
        print(f'서버 [{guild.name}]에 슬래시 커맨드 등록 실패: {e}')

@client.tree.command(name="공지삭제", description="현재 채널에서 선택한 공지사항 알림을 삭제합니다")
@app_commands.choices(type=[
    app_commands.Choice(name="SW학사공지", value="swAcademic"),
    app_commands.Choice(name="SW중심대학공지", value="sw")
])
async def unregister_notice(interaction: discord.Interaction, type: str):
    """현재 채널에서 선택한 유형의 공지사항 알림을 삭제합니다. (DM에서도 사용 가능)"""
    channel = interaction.channel
    
    # DM 채널인지 확인
    is_dm = isinstance(channel, discord.DMChannel)
    
    if not is_dm:  # 서버 채널인 경우
        # 관리자 권한 확인
        if not interaction.permissions.administrator:
            await interaction.response.send_message(
                "이 명령어는 관리자 권한이 필요합니다.",
                ephemeral=True
            )
            return

    # 크롤러 타입 매핑
    crawler_type_map = {
        "swAcademic": CrawlerType.SWACADEMIC,
        "sw": CrawlerType.SW
    }
    

    # 공지 타입 한글명 매핑
    notice_type_names = {
        "swAcademic": "SW학사공지",
        "sw": "SW중심대학 공지"
    }

    channel_id = str(interaction.channel_id)
    if client.crawler_config.remove_crawler(channel_id, crawler_type_map[type]):
        await interaction.response.send_message(
            f"이 채널에서 {notice_type_names[type]} 알림이 삭제되었습니다.",
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            f"이 채널에는 {notice_type_names[type]} 알림이 등록되어 있지 않습니다.",
            ephemeral=True
        )

def run_bot():
    client.run(os.getenv('DISCORD_TOKEN')) 