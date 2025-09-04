defmodule BorutaExampleWeb.ApiUsersController do
  use BorutaExampleWeb, :controller

  alias BorutaExample.Accounts

  def get_me(conn, _params) do
    user = conn.assigns.current_user
    IO.inspect(user, label: "User")
    if user do
      json(conn, %{user: user})
    else
      json(conn, %{"Error" => "User not found"})
    end
  end
end