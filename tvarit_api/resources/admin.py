from .base import Base


class Admin(Base):
    def __init__(self, api):
        super(Admin, self).__init__(api)
        self.api = api

    def settings(self):
        """

        :return:
        """
        path = "/admin/settings"
        r = self.api.GET(path)
        return r

    def stats(self):
        """

        :return:
        """
        path = "/admin/stats"
        r = self.api.GET(path)
        return r

    def create_user(self, user):
        """

        :param user:
        :return:
        """
        create_user_path = "/admin/users"
        r = self.api.POST(create_user_path, json=user)
        return r

    def change_user_password(self, user_id, password):
        """

        :param user_id:
        :param password:
        :return:
        """
        change_user_password_path = "/admin/users/%s/password" % user_id
        r = self.api.PUT(change_user_password_path, json={"password": password})
        return r

    def change_user_permissions(self, user_id, is_tvarit_admin):
        """

        :param user_id:
        :param is_tvarit_admin:
        :return:
        """
        change_user_permissions = "/admin/users/%s/permissions" % user_id
        r = self.api.PUT(
            change_user_permissions, json={"isGrafanaAdmin": is_tvarit_admin}
        )
        return r

    def delete_user(self, user_id):
        """

        :param user_id:
        :return:
        """
        delete_user_path = "/admin/users/%s" % user_id
        r = self.api.DELETE(delete_user_path)
        return r

    def pause_all_alerts(self, pause):
        """

        :param pause:
        :return:
        """
        change_user_permissions = self.path + "/pause-all-alerts"
        r = self.api.POST(change_user_permissions, json={"paused": pause})
        return r
