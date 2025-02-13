from discord import app_commands
import discord
from discord_bot.crawler_manager import CrawlerType
import os
from notice_entry import NoticeEntry
from datetime import datetime
from db_config import get_database
from discord.ext import commands

async def setup(bot):
    """테스트 관련 명령어들을 봇에 등록합니다."""

    @bot.tree.command(name="test", description="봇이 정상적으로 작동하는지 테스트합니다.")
    async def test(interaction: discord.Interaction):
        try:
            # MongoDB 연결 테스트
            db = get_database()
            collection = db['crawler_config']  # channels -> crawler_config로 수정
            
            # 채널 설정 확인
            channel_config = collection.find_one({'_id': str(interaction.channel_id)})
            if channel_config:
                crawlers = channel_config.get('crawlers', [])
                await interaction.response.send_message(
                    f"✅ 봇이 정상 작동 중입니다!\n"
                    f"이 채널에 등록된 크롤러: {', '.join(crawlers)}"
                )
            else:
                await interaction.response.send_message(
                    "✅ 봇이 정상 작동 중입니다!\n"
                    "아직 이 채널에 등록된 크롤러가 없습니다."
                )
                
        except Exception as e:
            await interaction.response.send_message(
                f"❌ 오류가 발생했습니다: {str(e)}"
            )

    @bot.tree.command(name="testnotice", description="[디버그] 선택한 채널/유저에게 테스트 공지사항을 전송합니다")
    @app_commands.choices(crawler=[
        app_commands.Choice(name="학사공지", value="academic"),
        app_commands.Choice(name="SW학사공지", value="swAcademic"),
        app_commands.Choice(name="SW중심대학공지", value="sw")
    ])
    async def test_notice(interaction: discord.Interaction, crawler: str):
        """[디버그] 선택한 채널/유저에게 테스트 공지사항을 전송합니다."""
        try:
            await interaction.response.defer(ephemeral=True)
            
            crawler_type_map = {
                "academic": CrawlerType.ACADEMIC,
                "swAcademic": CrawlerType.SWACADEMIC,
                "sw": CrawlerType.SW
            }
            
            # 등록된 채널/유저 목록 가져오기
            channels = bot.crawler_config.get_channels_for_crawler(crawler_type_map[crawler])
            if not channels:
                await interaction.followup.send(
                    f"선택한 {crawler} 알림에 등록된 채널이 없습니다.",
                    ephemeral=True
                )
                return

            # DB에서 최신 공지사항 가져오기
            db = get_database()
            collection = db[crawler]  # 각 크롤러 타입에 해당하는 컬렉션
            latest_notice = collection.find_one(
                sort=[('published', -1)]  # 작성일 기준 내림차순 정렬
            )
            
            if not latest_notice:
                await interaction.followup.send(
                    f"해당 크롤러의 공지사항이 DB에 없습니다.",
                    ephemeral=True
                )
                return

            # NoticeEntry 객체 생성
            test_notice = NoticeEntry({
                'title': latest_notice['title'],
                'link': latest_notice['link'],
                'published': datetime.fromisoformat(latest_notice['published']),
                'notice_type': latest_notice['notice_type']
            })

            # 채널/유저 정보 수집 및 선택 옵션 생성
            options = []
            for channel_id in channels:
                try:
                    channel = bot.get_channel(int(channel_id))
                    if not channel:  # DM 채널인 경우
                        user = await bot.fetch_user(int(channel_id))
                        label = f"DM: {user.name}"
                    else:  # 서버 채널인 경우
                        label = f"채널: {channel.guild.name} / #{channel.name}"
                    options.append(discord.SelectOption(
                        label=label[:100],  # Discord 제한: 최대 100자
                        value=channel_id,
                        description=f"ID: {channel_id}"[:100]
                    ))
                except Exception as e:
                    print(f"채널 정보 조회 실패 (ID: {channel_id}): {e}")

            if not options:
                await interaction.followup.send("유효한 채널/유저를 찾을 수 없습니다.", ephemeral=True)
                return

            # Select 메뉴 생성
            select = discord.ui.Select(
                placeholder="테스트 메시지를 보낼 채널/유저 선택",
                options=options,
                max_values=1
            )

            # 콜백 함수 정의
            async def select_callback(interaction: discord.Interaction):
                channel_id = select.values[0]
                try:
                    from discord_bot.discord_bot import send_notice
                    await send_notice(test_notice, crawler_type_map[crawler])
                    await interaction.response.send_message(
                        f"테스트 공지사항을 전송했습니다!\n"
                        f"제목: {test_notice.title}\n"
                        f"채널 ID: {channel_id}",
                        ephemeral=True
                    )
                except Exception as e:
                    await interaction.response.send_message(
                        f"공지사항 전송 중 오류가 발생했습니다: {str(e)}",
                        ephemeral=True
                    )

            select.callback = select_callback

            # Select 메뉴 뷰 생성
            view = discord.ui.View()
            view.add_item(select)

            await interaction.followup.send(
                f"테스트할 최신 공지사항:\n제목: {test_notice.title}\n작성일: {test_notice.published.strftime('%Y-%m-%d')}\n\n"
                "전송할 채널/유저를 선택하세요:",
                view=view,
                ephemeral=True
            )

        except Exception as e:
            await interaction.followup.send(f"오류가 발생했습니다: {str(e)}", ephemeral=True)

    @bot.tree.command(name="test-list", description="선택한 크롤러로 등록된 유저, 채널 목록을 확인합니다")
    @app_commands.choices(crawler=[
        app_commands.Choice(name="학사공지", value="academic"),
        app_commands.Choice(name="SW학사공지", value="swAcademic"),
        app_commands.Choice(name="SW중심대학공지", value="sw")
    ])
    async def list_registered(interaction: discord.Interaction, crawler: str):
        """선택한 크롤러로 등록된 유저, 채널 목록을 확인합니다."""
        try:
            crawler_type_map = {
                "academic": CrawlerType.ACADEMIC,
                "swAcademic": CrawlerType.SWACADEMIC,
                "sw": CrawlerType.SW
            }
            
            channels = bot.crawler_config.get_channels_for_crawler(crawler_type_map[crawler])
            
            if not channels:
                await interaction.response.send_message(
                    f"선택한 {crawler} 알림에 등록된 채널이 없습니다.",
                    ephemeral=True
                )
                return

            # 등록된 유저와 채널 정보 수집
            registered_items = []
            for channel_id in channels:
                try:
                    channel = bot.get_channel(int(channel_id))
                    if not channel:  # DM 채널인 경우
                        print(f"DM 채널 ID: {channel_id}")
                        user = await bot.fetch_user(int(channel_id))
                        registered_items.append(f"- DM: {user.name}#{user.discriminator}")
                    else:  # 서버 채널인 경우
                        registered_items.append(f"- 채널: {channel.guild.name} / #{channel.name}")
                except Exception as e:
                    print(f"정보 조회 실패 (ID: {channel_id}): {e}")
            
            # 결과 메시지 생성
            result_message = f"**{crawler} 알림 등록 목록:**\n"
            result_message += "\n".join(registered_items) if registered_items else "등록된 항목 없음"
            
            await interaction.response.send_message(result_message, ephemeral=True)
                
        except Exception as e:
            print(f"목록 조회 중 오류 발생: {e}")
            await interaction.response.send_message(
                "목록 조회 중 오류가 발생했습니다.", 
                ephemeral=True
            ) 