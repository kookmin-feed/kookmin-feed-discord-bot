from discord import app_commands
import discord
from discord_bot.crawler_manager import CrawlerType

async def setup(bot):
    """공지 등록/삭제 관련 명령어들을 봇에 등록합니다."""
    
    @bot.tree.command(name="공지등록", description="공지사항 알림을 등록합니다")
    @app_commands.choices(crawler=[
        app_commands.Choice(name="학사공지", value="academic"),
        app_commands.Choice(name="SW학사공지", value="swAcademic"),
        app_commands.Choice(name="SW중심대학공지", value="sw")
    ])
    async def register_notice(interaction: discord.Interaction, crawler: str):
        """공지사항 알림을 등록합니다."""
        try:
            crawler_type_map = {
                "academic": CrawlerType.ACADEMIC,
                "swAcademic": CrawlerType.SWACADEMIC,
                "sw": CrawlerType.SW
            }
            
            # 크롤러 타입 한글명 매핑 추가
            notice_type_names = {
                "academic": "학사공지",
                "swAcademic": "SW학사공지",
                "sw": "SW중심대학 공지"
            }
            
            # DM에서 실행된 경우 사용자 ID를 저장
            if isinstance(interaction.channel, discord.DMChannel):
                channel_id = str(interaction.user.id)
                print(f"DM 채널에서 등록: 사용자 ID {channel_id}")
            else:
                channel_id = str(interaction.channel_id)
                print(f"서버 채널에서 등록: 채널 ID {channel_id}")
            
            if bot.crawler_config.add_crawler(channel_id, crawler_type_map[crawler]):
                message = f"{notice_type_names[crawler]} 알림이 등록되었습니다."
            else:
                message = f"이미 {notice_type_names[crawler]} 알림이 등록되어 있습니다."
                
            await interaction.response.send_message(message, ephemeral=True)
                
        except Exception as e:
            print(f"알림 등록 중 오류 발생: {e}")
            await interaction.response.send_message(
                "알림 등록 중 오류가 발생했습니다.", 
                ephemeral=True
            )

    @bot.tree.command(name="공지삭제", description="선택한 공지사항 알림을 삭제합니다")
    @app_commands.choices(type=[
        app_commands.Choice(name="학사공지", value="academic"),
        app_commands.Choice(name="SW학사공지", value="swAcademic"),
        app_commands.Choice(name="SW중심대학공지", value="sw")
    ])
    async def unregister_notice(interaction: discord.Interaction, type: str):
        """현재 채널에서 선택한 유형의 공지사항 알림을 삭제합니다."""
        try:
            # DM에서 실행된 경우 사용자 ID를 사용
            if isinstance(interaction.channel, discord.DMChannel):
                channel_id = str(interaction.user.id)
                print(f"DM 채널에서 삭제: 사용자 ID {channel_id}")
            else:
                # 서버 채널인 경우 관리자 권한 확인
                if not interaction.permissions.administrator:
                    await interaction.response.send_message(
                        "이 명령어는 관리자 권한이 필요합니다.",
                        ephemeral=True
                    )
                    return
                channel_id = str(interaction.channel_id)
                print(f"서버 채널에서 삭제: 채널 ID {channel_id}")

            # 크롤러 타입 매핑
            crawler_type_map = {
                "academic": CrawlerType.ACADEMIC,
                "swAcademic": CrawlerType.SWACADEMIC,
                "sw": CrawlerType.SW
            }
            
            # 공지 타입 한글명 매핑
            notice_type_names = {
                "academic": "학사공지",
                "swAcademic": "SW학사공지",
                "sw": "SW중심대학 공지"
            }

            if bot.crawler_config.remove_crawler(channel_id, crawler_type_map[type]):
                message = f"{notice_type_names[type]} 알림이 삭제되었습니다."
            else:
                message = f"{notice_type_names[type]} 알림이 등록되어 있지 않습니다."
            
            await interaction.response.send_message(message, ephemeral=True)
            
        except Exception as e:
            print(f"알림 삭제 중 오류 발생: {e}")
            await interaction.response.send_message(
                "알림 삭제 중 오류가 발생했습니다.", 
                ephemeral=True
            )

    @bot.tree.command(name="등록된공지", description="현재 등록된 공지사항 알림 목록을 보여줍니다")
    async def list_crawlers(interaction: discord.Interaction):
        """현재 채널에 등록된 공지사항 알림 목록을 보여줍니다."""
        try:
            # DM인지 서버 채널인지 확인
            if isinstance(interaction.channel, discord.DMChannel):
                channel_id = str(interaction.user.id)
                channel_type = "DM"
            else:
                channel_id = str(interaction.channel_id)
                channel_type = f"채널 #{interaction.channel.name}"

            # 등록된 크롤러 목록 가져오기
            crawlers = bot.crawler_config.get_channel_crawlers(channel_id)
            
            # 크롤러 타입 한글명 매핑
            crawler_names = {
                "academic": "학사공지",
                "swAcademic": "SW학사공지",
                "sw": "SW중심대학공지"
            }
            
            if crawlers:
                # 등록된 크롤러 목록을 한글명으로 변환
                crawler_list = [f"- {crawler_names.get(crawler, crawler)}" for crawler in crawlers]
                message = f"**현재 {channel_type}에 등록된 알림:**\n" + "\n".join(crawler_list)
            else:
                message = f"현재 {channel_type}에 등록된 알림이 없습니다."
                
            await interaction.response.send_message(message, ephemeral=True)
            
        except Exception as e:
            print(f"알림 목록 조회 중 오류 발생: {e}")
            await interaction.response.send_message(
                "알림 목록 조회 중 오류가 발생했습니다.", 
                ephemeral=True
            ) 